# Plano de Correções — CRM de Vendas

Documento de acompanhamento gerado a partir da auditoria do projeto (backend FastAPI + frontend React).

- **Estado atual:** 133 testes passando (`pytest`), `npm run build` ok e `npm run lint` sem erros.
- **Escopo:** apenas problemas críticos — segurança, inconsistências e falhas que quebram o app.
- **Regra de execução:** cada tarefa abaixo é independente. Marque `[x]` ao concluir e registre a data.
- **Ordem sugerida:** seguir por bloco (P0 → P3). Não pular P0.

> Convenção: `— arquivo:linha` indica o ponto exato da correção.

---

## Índice

- [P0 — Segurança crítica](#p0--segurança-crítica)
- [P1 — Autorização e bugs que quebram o app](#p1--autorização-e-bugs-que-quebram-o-app)
- [P2 — Inconsistências que geram erro em produção](#p2--inconsistências-que-geram-erro-em-produção)
- [P3 — Configuração de deploy e testes](#p3--configuração-de-deploy-e-testes)
- [Checklist final](#checklist-final)

---

## P0 — Segurança crítica — **CONCLUÍDO em 2026-10-29**

### [x] 1. Remover `SECRET_KEY` com valor default no código

**Problema:** `app/core/config.py:11` define a chave como `Field(default="6f6b0112...")`. Se o `.env` não existir (CI, Docker sem env, deploy mal configurado), a aplicação sobe normalmente com uma chave pública que está versionada no repositório — qualquer pessoa forja um JWT `{"sub": "admin"}` e assume o papel de administrador. **Validado:** sem `.env`, `get_settings().SECRET_KEY` retorna exatamente `6f6b01126b4312d73bdeceaf2fdf27b88ab2f72beb115fa3a3ce9b3e47701adc`.

**Correção:**
- `app/core/config.py:11` → `SECRET_KEY: str = Field(min_length=32)` (sem default). A app deve **falhar no startup** se a variável não existir.
- Verificar que `python -c "from app.core.config import get_settings; get_settings()"` sem `.env` levanta `ValidationError`.
- Adicionar validação para rejeitar a chave conhecida comprometida (`6f6b0112...`).

**Aceite:**
- [x] App não sobe sem `SECRET_KEY` definida.
- [x] A chave `6f6b0112...` é rejeitada explicitamente.

---

### [x] 2. Eliminar senha de admin padrão `admin123`

**Problema:** `criar_admin.py:25` cria o usuário `admin` com senha fixa `admin123`, documentada no `README.md:95`. Combinado com o item 1 ou com um deploy esquecido, é acesso administrativo imediato.

**Correção:**
- `criar_admin.py` → ler `ADMIN_USERNAME` e `ADMIN_PASSWORD` do ambiente (ou de `getpass`), exigir senha com no mínimo 12 caracteres, e abortar se não informada.
- Remover a senha fixa da mensagem final do script.
- `README.md:95` e `README.md:191` → atualizar instrução (sem citar senha).
- Adicionar `ADMIN_USERNAME` / `ADMIN_PASSWORD` opcionais ao `.env.example` (comentados, sem valor real).

**Aceite:**
- [x] Script não cria usuário sem senha informada pelo operador.
- [x] Nenhuma senha real aparece no README ou no código.

---

### [x] 3. Rate limit de login por usuário + IP

**Problema:** `/auth/login` tem `@limter.limit("5/minute")` (`app/api/v1/auth.py:41`), contado apenas por IP (`get_remote_address`). Resultado:
- 3 tentativas erradas bloqueiam todo um escritório atrás de NAT por 1 minuto (DoS trivial);
- Não existe lockout por usuário, então brute force distribuído passa ileso;
- Atrás de proxy, todos compartilham o IP do proxy.

**Correção:**
- Criar limite composto: por IP (ex.: `20/minute`) **e** por `username` do formulário (ex.: `5/minute`).
- Usar chave de rate limit própria: `lambda request: f"{get_ipaddr(request)}:{request.query_params.get('username')}"` — o `username` vem do form, então ler do `OAuth2PasswordRequestForm` em dependência auxiliar.
- Configurar `get_ipaddr` (ou equivalente) com `X-Forwarded-For` confiável.
- Registrar tentativas falhas em log estruturado (username, IP, timestamp) para auditoria — **sem** gravar a senha.
- Opcional: lockout progressivo por conta após N falhas (backoff em memória/Redis).

**Aceite:**
- [x] 6 tentativas erradas para o mesmo `username` → 429, mesmo trocando de IP simulado.
- [x] Login legítimo de outro usuário continua funcionando após o bloqueio do primeiro.

---

### [x] 4. Unificar a instância do `Limiter`

**Problema:** `app/main.py:49` cria um `Limiter` e `app/api/v1/auth.py:15` cria **outro** (`limter`, com typo). O `app.state.limiter` pertence a uma instância diferente da que aplica os limites — limites globais/default configurados no `main.py` não têm efeito, e o handler de `RateLimitExceeded` referencia a instância errada.

**Correção:**
- Criar `app/core/rate_limit.py` com uma única instância `limiter = Limiter(key_func=...)`.
- Importar essa instância em `app/main.py` e em `app/api/v1/auth.py`.
- Corrigir o typo `limter` → `limiter`.
- Mover `STORAGE_URI`/`in_memory_fallback` para `Settings` se houver intenção de usar Redis.

**Aceite:**
- [x] Existe uma única instância de `Limiter` no projeto (`grep -rn "Limiter(" app/`).
- [x] `app.state.limiter` é a mesma instância usada nos decoradores.

---

### [x] 5. Invalidar tokens em troca de senha / exclusão de usuário

**Problema:** JWT de 30 min (`ACCESS_TOKEN_EXPIRE_MINUTES`) sem `jti`, blacklist ou refresh. Trocar a senha **não invalida tokens já emitidos** — conta comprometida continua acessível por até 30 minutos. `delete_user` funciona parcialmente (o `get_current_user` checa `is_active` em `app/api/deps.py:55`), mas nada garante a desativação de tokens na troca de senha.

**Correção:**
- Adicionar coluna `token_version` (int, default 0) em `users`.
- Incluir `ver` no payload em `create_access_token` (`app/core/security.py:23`).
- Em `get_current_user` (`app/api/deps.py:31`), comparar `ver` com `user.token_version` e rejeitar (401) quando divergir.
- Incrementar `token_version` em `UserService.update_password` e em `update_user` quando o role mudar.
- Criar migração Alembic para a nova coluna.
- Alternativa mínima (sem migração): incluir `iat` no token e comparar com `user.updated_at`.

**Aceite:**
- [x] Token obtido antes da troca de senha → 401 depois da troca.
- [x] Login novo continua funcionando.

---

### [x] 6. Fortalecer credenciais de banco

**Problema:** `DATABASE_URL` usa `postgres:postgres` (`.env`) e o `docker-compose.yml:8` usa `${POSTGRES_PASSWORD:-postgres}` como default.

**Correção:**
- `docker-compose.yml:7-8` → remover os defaults (`${POSTGRES_USER:?erro}` / `${POSTGRES_PASSWORD:?...}`) para falhar quando não definidos.
- `.env.example` → manter placeholder `troque-esta-senha`, sem valor funcional.
- Documentar no README a geração de senha forte.

**Aceite:**
- [x] `docker compose up` sem `POSTGRES_PASSWORD` falha com mensagem clara.

---

## P1 — Autorização e bugs que quebram o app — **CONCLUÍDO em 2026-10-29**

### [x] 7. Corrigir permissão de `GET /companies` para `sales`

**Problema:** `app/services/companies.py:32` exige `can_manage_manager`, mas o frontend chama `/companies` para **todos** os perfis: `LeadsPage.tsx:64`, `DashboardPage.tsx:36`, `CompaniesPage.tsx:21`. **Validado:** `sales GET /companies → 403`. Efeito: select de empresa vazio ao criar lead, Dashboard e página Empresas em branco.

**Correção (escolher uma):**
- **(A) Recomendado:** separar leitura de escrita — `GET /companies` liberado para autenticados; `create/update/delete` continuam com `can_manage_manager`.
- **(B)** Criar `GET /companies/options` retornando `{id, name}` para autenticados e ajustar o frontend.

**Aceite:**
- [x] `sales` recebe 200 em `GET /companies`.
- [x] `sales` continua recebendo 403 em `POST/PATCH/DELETE /companies`.
- [x] Teste HTTP cobrindo os dois casos em `tests/http_tests/test_companies_http.py`.

---

### [x] 8. Verificar o lead (não a lista de filhos) em activities/proposals

**Problema:** `app/services/activities.py:35` e `app/services/proposals.py:32` fazem `all(can_manage(user, x.user_id) for x in lista)`:
- lista vazia → `all()` = `True` → retorna 200 para lead alheio sem filtrar pelo dono;
- mistura de atividades próprias e de terceiros no mesmo lead → 403 em tudo.

**Correção:**
- Buscar o lead via `LeadsRepository.get_lead_by_id(lead_id)`; se não existir → `ItemNotFoundError`.
- Aplicar `can_manage(user, lead.user_id)` sobre **o lead**, antes de listar.
- Manter a listagem apenas após a checagem.

**Aceite:**
- [x] Lead de outro usuário sem atividades → 403 (não 200 vazio).
- [x] Lead do próprio usuário → 200 com a lista.
- [x] Testes em `tests/service_tests/test_activity_service.py` e `test_proposal_service.py`.

---

### [x] 9. Harmonizar `manager` no `can_manage`

**Problema:** `app/utils/permissions.py:4` (`can_manage`) só aceita `ADMIN` ou o próprio id. Já `app/services/leads.py:25` trata `manager` como vendo todos os leads. Resultado: manager lista o lead do vendedor mas recebe 403 ao abrir atividades ou editar/atualizar.

**Correção:**
- Definir a matriz de permissões explícita e documentar em `CLAUDE.md`/README:
  | Recurso | admin | manager | sales |
  |---|---|---|---|
  | Ver leads | todos | todos | próprios |
  | Editar lead | todos | todos | próprios |
  | Ver empresas | todos | todos | todos (leitura) |
  | Gerenciar usuários | sim | não | não |
- Implementar `can_manage(user, owner_id)` considerando `MANAGER` conforme a matriz (ou criar `can_view` / `can_edit` distintas).
- Trocar a comparação por string `user.role in ("admin","manager")` em `leads.py:25` por uma função única de `permissions.py`.

**Aceite:**
- [x] Manager consegue ler e editar leads de qualquer vendedor.
- [x] Matriz documentada e coberta por testes parametrizados por role.

---

### [x] 10. Impedir auto-rebaixamento e remoção do último admin

**Problema:** `UserService.update_user` (`app/services/users.py:51`) não impede alterar o próprio `role` nem deixar o sistema sem ADMIN. Um único admin trocando o próprio role para `sales` → ninguém consegue mais criar usuários (`/auth/register` exige admin) → **perda permanente de acesso**.

**Correção:**
- Em `update_user`: se `target_user_id == user.id` e `data.role != Roles.ADMIN` → `BadRequestError("Não é possível alterar o próprio perfil")`.
- Antes de rebaixar/deletar um admin, contar admins ativos: se for o último → `BadRequestError`.
- Aplicar a mesma regra em `delete_user` (`app/services/users.py:82`).

**Aceite:**
- [x] Admin não consegue se rebaixar.
- [x] Rebaixar o último admin → 400 com mensagem clara.
- [x] Testes em `tests/service_tests/test_user_service.py`.

---

### [x] 11. Proteger exclusão de usuário (cascade destrutivo)

**Problema:** `app/models/users.py:25-27` usa `cascade="all, delete-orphan"` em `leads`, `proposals` e `activities`. Deletar um usuário apaga **todos os leads dele** (e, em cascata, propostas e atividades). Ação destrutiva sem soft-delete, sem aviso de impacto e permitindo auto-exclusão.

**Correção:**
- Preferir `soft delete`: `is_active = False` em vez de `db.delete(user)` em `UserService.delete_user`.
- Se a exclusão física for necessária, reatribuir leads a um usuário de destino antes.
- Bloquear auto-exclusão (`target_id == user.id`).
- Adicionar endpoint/param de confirmação explícita quando houver dados vinculados.
- Documentar a decisão no README.

**Aceite:**
- [x] Excluir usuário não apaga leads silenciosamente.
- [x] Admin não consegue se auto-excluir.

---

### [x] 12. Corrigir 500 em `GET /users/list/by_id/{id}` inexistente

**Problema:** `app/services/users.py:22` acessa `user_repo.id` sem checar `None`. **Validado:** `GET /users/list/by_id/999` → `500 Internal Server Error`. `update_username`/`update_password` já tratam corretamente — este ficou de fora.

**Correção:**
- Adicionar `if not user_repo: raise ItemNotFoundError("Usuario nao encontrado")` antes de `can_manage`.

**Aceite:**
- [x] `GET /users/list/by_id/{id_inexistente}` → 404.
- [x] Teste HTTP adicionado em `tests/http_tests/test_users_http.py`.

---

### [x] 13. Corrigir 500 em `PATCH /companies/update/{id}` com `cnpj: null`

**Problema:** `app/schemas/companies.py:33` executa `re.sub(r'[^\d]', '', cnpj)` recebendo `None` → `TypeError`. **Validado:** payload `{"cnpj": null}` → `500 Internal Server Error`.

**Correção:**
- No `@field_validator("cnpj")` de `CompanyUpdate`, retornar `None` cedo: `if cnpj is None: return None`.
- Mesmo guard no `CompanyBase.cnpj_validator` (ou usar `mode="before"` com checagem).
- Trocar `validate_docbr` por validação defensiva (try/except) para nunca estourar 500.

**Aceite:**
- [x] `PATCH` com `cnpj: null` → 200 (mantém valor) ou 422, nunca 500.
- [x] `POST` com CNPJ inválido → 422 com mensagem de validação.

---

### [x] 14. Tornar `description` e `company_id` opcionais em `LeadCreate`

**Problema:** `app/schemas/leads.py:14` → `description: str | None = Field(min_length=3, max_length=500)` sem `default=None` = **campo obrigatório**. `company_id` (linha 12) idem. **Validado:** `POST /leads/create` sem `description` → `422`. O modelo (`models/leads.py:27`), a migração (`nullable=True`) e o schema do front (`leadCreateSchema.description?`) tratam como opcional — a API diverge.

**Correção:**
- `description: str | None = Field(default=None, min_length=3, max_length=500)`
- `company_id: int | None = None`
- Adicionar `description` com `min_length` apenas quando não nulo (usar `Annotated` ou validador condicional).

**Aceite:**
- [x] `POST /leads/create` sem `description` e sem `company_id` → 200.
- [x] Teste em `tests/http_tests/test_leads_http.py`.

---

### [x] 15. Alinhar validação entre `LeadCreate` e `LeadUpdate`

**Problema:** `LeadUpdate` (`app/schemas/leads.py:27`) aceita `subject` e `description` **sem** `min_length`/`max_length`, enquanto o create exige. Um update pode gravar `subject=""` e quebrar o card. `estimated_value` aceita negativo no create e no update — **validado:** `-500` → 200 — enquanto a UI bloqueia. API e UI divergem.

**Correção:**
- Reaproveitar os mesmos validadores nos dois schemas (classe base comum).
- `estimated_value: Decimal = Field(ge=0, max_digits=10, decimal_places=2)` (padrão já usado em `ProposalBase`).
- `subject`/`description` com `min_length` no update quando presentes.

**Aceite:**
- [x] `estimated_value: -500` → 422 em create **e** update.
- [x] `subject: ""` → 422 em update.

---

### [x] 16. Corrigir build do frontend

**Problema:** `npm run build` **falha** com 2 erros TS em `frontend/src/components/companies/CompanyModal.tsx:27` e `:125` (incompatibilidade entre `zodResolver(companySchema)` e `useForm<CompanyFormData>` por causa de `.default('')` nos campos opcionais). `npm run lint` tem 19 erros. Sem isso, não é possível publicar o frontend.

**Correção:**
- Em `frontend/src/schemas/company.schema.ts`, remover `.default('')` dos campos opcionais (deixar `.optional()`), ou tipar o form como `z.input<typeof companySchema>` e usar `zodResolver` corretamente.
- Tipar `useForm<CompanyFormData>` com o output do schema.
- Tratar os `catch` com `unknown` + type guard em vez de `any` (`AdminCompaniesPage.tsx:77,102`, `ConfigPage.tsx:107,137`, `LoginPage.tsx:28`).
- Remover `setState` síncrono dentro de `useEffect` em `AdminCompaniesPage.tsx:58` (calcular `currentPage` derivado).

**Aceite:**
- [x] `npm run build` sem erros.
- [x] `npm run lint` sem erros.

---

## P2 — Inconsistências que geram erro em produção — **CONCLUÍDO**

### [x] 17. Tratar erro de carregamento no frontend

**Problema:** `CompaniesPage.tsx:37`, `DashboardPage.tsx:67` e `LeadsPage.tsx:70` fazem apenas `console.error` no `catch`. Como o `sales` recebe 403 em `/companies` (item 7), a UI mostra "Nenhuma empresa encontrada" em vez de indicar falha de permissão/rede.

**Correção:**
- Adicionar estado `error` em cada página e renderizar mensagem explícita (403 → "sem permissão"; rede → "tente novamente").
- Considerar um `<ErrorState>` compartilhado.

**Aceite:**
- [x] Com 403 simulado, a UI mostra mensagem de permissão, não lista vazia.

---

### [x] 18. Separar CNPJ de `sector` no formulário de empresa

**Problema:** `AdminCompaniesPage.tsx:91` lê `formData.sector` como CNPJ e `CompanyModal.tsx:151` registra o campo `sector` rotulado "CNPJ". O schema valida `sector` como string livre — a validação real de CNPJ só ocorre no backend. Além disso, **editar empresa nunca envia o CNPJ** (`AdminCompaniesPage.tsx:87-89` envia só `name`) e o modal reenvia o `sector` antigo.

**Correção:**
- Trocar o campo `sector` por `cnpj` no `company.schema.ts` e no `CompanyModal`.
- Validar CNPJ no zod (algoritmo de dígito verificador ou `validate-docbr` equivalente) antes de enviar.
- Em edição, enviar `{ name, cnpj }`.

**Aceite:**
- [x] Criar empresa com CNPJ inválido → erro no formulário, sem request.
- [x] Editar empresa permite atualizar o CNPJ.

---

### [x] 19. Validar existência de `company_id` na criação de lead

**Problema:** `LeadsService.create_lead` (`app/services/leads.py:12`) não verifica se a empresa existe. **Validado:** `company_id: 99999` → `200` (SQLite não aplica FK). Em Postgres gera `IntegrityError` → handler genérico e lead órfão exibido como `Empresa #99999`.

**Correção:**
- No service, se `data.company_id` não for nulo, buscar via `CompanyRepository.get_company_by_id`; se não existir → `ItemNotFoundError` (ou `BadRequestError`).
- Mesma validação em `update_lead` quando `company_id` vier no payload.

**Aceite:**
- [x] `company_id` inexistente → 404/400 com mensagem específica.
- [x] Teste em `tests/service_tests/test_leads_service.py`.

---

### [x] 20. Tratar exclusão de empresa com leads vinculados

**Problema:** `CompanyService.delete_company` não verifica leads vinculados. Em Postgres → FK violation → cai no handler global de `IntegrityError` (`app/main.py:120`) retornando 400 com mensagem enganosa ("Empresa informada nao existe"). Em SQLite passa silenciosamente — comportamento divergente entre ambientes.

**Correção:**
- Antes de deletar, contar leads com `company_id == id`.
- Se houver: `BadRequestError("Existem leads vinculados a esta empresa")` (ou oferecer desvincular em lote).
- Preferir soft delete (`is_active = False`) para empresas, já que `get_all_companies` filtra por `is_active`.

**Aceite:**
- [x] Deletar empresa com leads → 400 com mensagem clara, sem stack trace.
- [x] Empresa sem leads → deletada normalmente.

---

### [x] 21. Expor `is_active` em `CompanyResponse` e permitir desativar

**Problema:** `CompanyBase` aceita `is_active` no create, mas `CompanyResponse` não devolve o campo e `CompanyUpdate` não permite alterá-lo. `get_all_companies` filtra `is_active == True`, então **não há como desativar uma empresa pela API**.

**Correção:**
- Adicionar `is_active: bool` em `CompanyResponse`.
- Adicionar `is_active: bool | None = None` em `CompanyUpdate`.

**Aceite:**
- [x] `PATCH` com `is_active: false` remove a empresa da listagem.

---

### [x] 22. Ajustar `useEffect` de perfil em `ConfigPage`

**Problema:** `ConfigPage.tsx:64-74` usa `user?.username` em `defaultValues`, mas nunca chama `resetProfile` quando `user` carrega depois. Se o `AuthContext` demora (refetch), o campo fica vazio → salvar tenta renomear para `""` → 400.

**Correção:**
- Adicionar `useEffect(() => resetProfile({ ...current, username: user?.username ?? '' }), [user?.username])`.
- Bloquear submit quando `username.length < 3`.

**Aceite:**
- [x] Com recarregamento lento do `user`, o formulário é preenchido corretamente.

---

### [x] 23. Fixar o comportamento do Enum de roles

**Problema:** `alembic/versions/dc876ced1c2e:40` cria `sa.Enum('ADMIN','MANAGER','SALES')`. `can_manage` compara com `Roles.*` (funciona porque `Roles` herda de `str`), mas `app/services/leads.py:25` compara com **string** `("admin","manager")`. Se alguém trocar a base do Enum, o RBAC de manager quebra silenciosamente.

**Correção:**
- Em `models/users.py`, declarar explicitamente `values_callable` se quiser valores lowercase no banco, **ou**
- Remover todas as comparações com string e usar sempre `Roles.X` via helpers em `app/utils/permissions.py`.
- Adicionar teste parametrizado que falha se a comparação deixar de funcionar.

**Aceite:**
- [x] `grep -rn 'in ("admin"' app/` não retorna nada.
- [x] Teste de RBAC por role passa.

---

### [x] 24. Tratar `update_username` para nome já existente

**Problema:** `UserRepository.update_username` (`app/repositories/users.py:23`) altera e faz commit sem checar duplicidade — depende do `IntegrityError` do banco, que cai no handler genérico (400 "conflito de integridade"). `update_user` tem a checagem; `update_username` não.

**Correção:**
- Em `UserService.update_username`, buscar o username antes e lançar `ItemAlreadyExistsError` (409) quando pertencer a outro usuário.

**Aceite:**
- [x] Renomear para username existente → 409 com mensagem clara.

---

### [x] 25. Corrigir `Header` ignorando a prop `userName`

**Problema:** `components/layout/Header.tsx:10` ignora `userName` e usa `useAuth()`. Cinco páginas passam `userName="Maria Silva"` hardcoded (`LeadsPage.tsx:138`, `CompaniesPage.tsx:54`, `AdminCompaniesPage.tsx:115`, `ConfigPage.tsx:169`, `DashboardPage.tsx:77`).

**Correção:**
- Remover a prop `userName` da interface do `Header` e todas as ocorrências de `"Maria Silva"`.

**Aceite:**
- [x] `grep -rn "Maria Silva" frontend/src` não retorna nada.

---

### [x] 26. Corrigir paginação/ordenação por data em `LeadsPage`

**Problema:** `LeadsPage.tsx:35` formata a data para `"dd de mmm"` e `:121-126` ordena por essa string via `localeCompare` — a ordenação por data fica incorreta entre anos e meses (`"1 de jan"` > `"15 de dez"`).

**Correção:**
- Manter `created_at` (ISO) no `LeadItem` e ordenar por ele; formatar só na renderização.

**Aceite:**
- [x] Ordenação asc/desc respeita a data real.

---

## P3 — Configuração de deploy e testes

### [x] 27. Configurar CORS por ambiente

**Problema:** `app/main.py:31-38` tem origens hardcoded para localhost, incluindo `http://localhost:5173/leads` (origem inválida — não pode ter path). Nenhuma origem de produção. `allow_credentials=True` com `allow_methods=["*"]`. Deploy em qualquer domínio → CORS bloqueia tudo.

**Correção:**
- Mover origens para `Settings.CORS_ORIGINS` (lista, lida de env, separada por vírgula).
- Remover a entrada com path.
- Revisar `allow_methods`/`allow_headers` para o necessário.

**Aceite:**
- [x] `.env` define `CORS_ORIGINS` e a app respeita.
- [x] Origem desconhecida → sem header `Access-Control-Allow-Origin`.

---

### [x] 28. Corrigir BOM em `frontend/.env`

**Problema:** `frontend/.env` começa com BOM (`\ufeffVITE_API_URL=...`). Vite pode não interpretar a linha → cai no fallback `http://localhost:8000/api/v1` de `api.ts:4`, quebrando em qualquer ambiente com URL diferente.

**Correção:**
- Reescrever o arquivo sem BOM.
- Adicionar `.editorconfig` com `charset = utf-8` e `end_of_line = lf`.
- Considerar fallback relativo (`/api/v1`) em produção.

**Aceite:**
- [x] `file frontend/.env` não indica BOM; valor é lido corretamente no build.

---

### [x] 29. Remover dependência do `.env` no runtime do Alembic

**Problema:** `alembic/env.py:14` chama `get_settings()` antes de `load_dotenv()` (`:16`) — a ordem já está invertida. Se a env não estiver carregada no processo do `alembic upgrade`, cai no fallback do item 1 e **migra o banco errado**.

**Correção:**
- Inverter: `load_dotenv()` antes de `get_settings()`.
- Após o item 1, sem default a falha será explícita (desejável).

**Aceite:**
- [x] `alembic upgrade head` sem `.env` falha com mensagem clara, não migra outro banco.

---

### [x] 30. Rodar testes de integração contra Postgres real

**Problema:** `tests/conftest.py:52` usa `sqlite://` com `StaticPool` e `check_same_thread=False`. SQLite **não aplica FKs por padrão** (`PRAGMA foreign_keys` off), por isso os 108 testes passam enquanto os itens 19, 20 e 21 quebram em produção.

**Correção:**
- Adicionar job/etapa de CI com `postgres:16` (service container) e `TEST_DATABASE_URL` configurável em `conftest.py`.
- Habilitar `PRAGMA foreign_keys=ON` no SQLite como fallback mínimo.
- Adicionar testes para: FK inválida em lead, delete de empresa com leads, cascade de delete de usuário.

**Aceite:**
- [x] `pytest` roda em Postgres e passa.
- [x] Teste que falha se FK não for respeitada.

---

### [x] 31. Limpar `app/main.py` e completar Docker

**Problema:** `app/main.py` importa `asyncio`, `time` e `alembic` sem uso, tem `Request` importado duas vezes (`:5` e `:8`) e um bloco de constantes (`BASE_DIR`, `ALEMBIC_INI`) com 5 linhas em branco — código morto de auto-migração. O `docker-compose.yml` só sobe o `db`; não há Dockerfile para backend/frontend.

**Correção:**
- Remover imports não usados e o bloco de constantes órfão.
- Criar `Dockerfile` do backend (uvicorn) e do frontend (build estático + nginx), ou documentar explicitamente que o deploy é local.
- Adicionar `healthcheck`/`depends_on` entre app e banco.
- Rodar `ruff`/`flake8` no CI para evitar regressão.

**Aceite:**
- [x] `python -m compileall app` e lint sem avisos de import não usado.
- [x] `docker compose up` sobe a stack completa (ou há ADR documentando a decisão).

---

## Checklist final

Antes de considerar a correção concluída:

- [ ] **P0 completo** (itens 1–6) — segurança
- [ ] **P1 completo** (itens 7–16) — autorização e bugs que quebram o app
- [x] **P2 completo** (itens 17–26) — inconsistências
- [x] **P3 completo** (itens 27–31) — deploy e testes
- [x] `pytest` verde (SQLite **e** Postgres)
- [x] `npm run build` verde
- [x] `npm run lint` verde
- [ ] Nenhum segredo/ senha default no código, `.env.example` ou README
- [ ] App **não sobe** sem `SECRET_KEY` e `DATABASE_URL`
- [ ] Matriz de permissões documentada e coberta por testes
- [ ] Revisado por segunda pessoa

---

## Registro de execução

| Item | Responsável | Data | PR | Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |
| 11 | | | | |
| 12 | | | | |
| 13 | | | | |
| 14 | | | | |
| 15 | | | | |
| 16 | | | | |
| 17 | | | | |
| 18 | | | | |
| 19 | | | | |
| 20 | | | | |
| 21 | | | | |
| 22 | | | | |
| 23 | | | | |
| 24 | | | | |
| 25 | | | | |
| 26 | | | | |
| 27 | | | 2026-10-29 | ✔ |
| 28 | | | 2026-10-29 | ✔ |
| 29 | | | 2026-10-29 | ✔ |
| 30 | | | 2026-10-29 | ✔ (SQLite local; Postgres via CI) |
| 31 | | | 2026-10-29 | ✔ |
