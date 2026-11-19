# CRM de Vendas

Aplicacao web para gerenciamento de leads, empresas, propostas, atividades comerciais e usuarios. O projeto possui uma API REST em FastAPI, interface em React e persistencia em PostgreSQL.

## Funcionalidades

- Autenticacao com JWT e limite de 5 tentativas de login por minuto para cada combinacao `IP + username`.
- Invalidação de tokens ao trocar a senha ou alterar o perfil (`role`) via `token_version`. A troca de username também invalida tokens antigos na prática, porque o `sub` do JWT deixa de corresponder a um usuário existente.
- Controle de usuarios com os perfis `admin`, `manager` e `sales`.
- Cadastro, listagem, atualizacao e remocao de empresas e leads.
- Busca de leads por nome/e-mail/telefone, filtro por status, ordenacao por data e paginacao.
- Acompanhamento de atividades por lead: ligacao, reuniao, e-mail, WhatsApp e outros.
- Cadastro e acompanhamento de propostas comerciais.
- Dashboard para visualizacao dos leads e empresas recentes.
- Regras de permissao para restringir a gestao de recursos conforme o perfil do usuario.

### Matriz de permissoes por perfil

| Recurso | admin | manager | sales |
| --- | --- | --- | --- |
| Ver leads | todos | todos | proprios |
| Editar lead | todos | todos | proprios |
| Ver atividades/propostas de um lead | todos | todos | proprios |
| Ver empresas | todos | todos | todos (leitura) |
| Criar/editar/deletar empresas | sim | sim | nao |
| Gerenciar **outros** usuarios (role, username, senha) | sim | nao | nao |
| Alterar o proprio username/senha | sim | sim | sim |
| Alterar o proprio `role` | nao | nao | nao |
| Alterar `role` de terceiros | sim | nao | nao |

A implementacao vive em `app/utils/permissions.py`. Apenas um admin pode alterar perfis;
nenhum admin pode rebaixar o proprio perfil, se auto-excluir ou deixar o sistema sem um
administrador ativo (a exclusao de usuario e um soft delete: o usuario fica inativo e seus
leads, propostas e atividades sao preservados).

> **Nota sobre a interface:** na UI atual, apenas o perfil `admin` acessa a tela com
> criacao/edicao/exclusao de empresas (`AdminCompaniesPage`). O backend permite que `manager`
> escreva em `/companies`, mas a UI ainda entrega a tela somente leitura (`CompaniesPage`)
> para esse perfil.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, slowapi (rate limiting) |
| Banco de dados | PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Zod, React Hook Form, axios |
| Testes | Pytest, GitHub Actions (CI) |
| Infraestrutura local | Docker Compose |

## Estrutura

```text
app/                 API FastAPI
  api/               Rotas, dependencias e excecoes de dominio (exceps.py)
  core/              Configuracao, seguranca e rate limiting
  db/                Conexao e base do SQLAlchemy
  models/            Modelos ORM
  repositories/      Acesso a dados
  schemas/           Contratos Pydantic
  services/          Regras de negocio
  utils/             Permissoes (permissions.py)
alembic/             Migracoes do banco de dados
db/init/             Scripts executados na inicializacao do container PostgreSQL
                     (schema e permissoes)
docs/adr/            Decisoes de arquitetura (ADR-001-deploy-local)
frontend/            Aplicacao React
tests/               Testes de servico, HTTP e integracao
criar_admin.py       Script de criacao do usuario administrador inicial
```

## Pre-requisitos

- Python 3.12 ou superior (o CI usa Python 3.13)
- Node.js 20 ou superior (o CI usa Node 22)
- Docker Desktop com Docker Compose

## Configuracao

Crie um arquivo `.env` na raiz do projeto. A aplicacao espera as variaveis abaixo:

```env
APP_NAME=CRM de vendas
DEBUG=false
SECRET_KEY=troque-por-uma-chave-secreta-com-pelo-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+psycopg2://postgres:troque-esta-senha@localhost:5432/CRM
POSTGRES_USER=postgres
POSTGRES_PASSWORD=troque-esta-senha
# Origens CORS permitidas, separadas por vírgula (sem path na URL).
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Opcionais — lidas por criar_admin.py (se ausentes, o script pede no terminal)
# ADMIN_USERNAME=
# ADMIN_PASSWORD=

# Opcional — usada apenas pelos testes de integracao
# TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/crm_test
```

`SECRET_KEY` deve ser exclusiva e mantida fora do controle de versao. O arquivo `.env` ja esta ignorado pelo Git.

O arquivo `.env.example` na raiz e a referencia para os nomes e valores esperados. As variaveis
`APP_NAME`, `DEBUG`, `ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES` tem valores padrao no codigo
(`app/core/config.py`) e so precisam ser definidas quando for necessario sobrescrever esses valores.

## Execucao local

### 1. Inicie o banco de dados

Na raiz do projeto:

```powershell
docker compose up -d db
```

O PostgreSQL ficara disponivel em `localhost:5432`.

### 2. Prepare e execute o backend

Ainda na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

A API sera iniciada em `http://localhost:8000`. A documentacao interativa pode ser acessada em `http://localhost:8000/docs`.

### 3. Crie o usuario administrador inicial

Com o ambiente virtual ativo e as migracoes aplicadas:

```powershell
python criar_admin.py
```

O script le as credenciais de `ADMIN_USERNAME` e `ADMIN_PASSWORD` (variaveis de ambiente) ou as solicita no terminal. A senha deve ter no minimo 12 caracteres. Nenhuma senha padrao e criada — defina uma senha forte no momento da criacao.

### 4. Execute o frontend

Em outro terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

O Vite exibira a URL local, normalmente `http://localhost:5173`. Por padrao, o frontend consome `http://localhost:8000/api/v1`.

Para apontar a interface para outra instancia da API, crie `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## API

Todas as rotas da aplicacao usam o prefixo `/api/v1`. Com excecao de `POST /auth/login` e da rota
raiz `GET /` (publica, apenas para verificacao), as rotas exigem o cabecalho `Authorization: Bearer <token>`.

| Modulo | Endpoints disponiveis |
| --- | --- |
| Autenticacao | `POST /auth/login`, `POST /auth/register` |
| Usuarios | `GET /users/me`, `GET /users`, `GET /users/list/by_id/{id}`, `PATCH /users/update_username/{id}`, `PATCH /users/update/{id}`, `PATCH /users/update_password/{id}`, `DELETE /users/delete/{id}` |
| Leads | `GET /leads`, `POST /leads/create`, `PATCH /leads/update/{id}`, `DELETE /leads/delete/{id}` |
| Empresas | `GET /companies`, `POST /companies/create`, `PATCH /companies/update/{id}`, `DELETE /companies/delete/{id}` |
| Atividades | `GET /activities/lead_id/{lead_id}`, `POST /activities/create`, `PATCH /activities/update/{id}`, `DELETE /activities/delete/{id}` |
| Propostas | `GET /proposals/lead_id/{lead_id}`, `POST /proposals/create`, `PATCH /proposals/update/{id}`, `DELETE /proposals/delete/{id}` |

Principais estados aceitos:

- Leads: `new`, `contacted`, `lost`, `won`.
- Propostas: `pending`, `accepted`, `rejected`.
- Atividades: `call`, `meeting`, `email`, `whatsapp`, `other`.

### Observacoes de autorizacao

| Endpoint | Regra |
| --- | --- |
| `GET /` | Publico; rota de verificacao, fora de `/api/v1`. |
| `POST /auth/register` | Exige usuario autenticado com perfil `admin`. |
| `GET /users` | Exige perfil `admin`. |
| `GET /users/list/by_id/{id}` | Admin ou o proprio usuario. |
| `PATCH /users/update_username/{id}` | Admin ou o proprio usuario. |
| `PATCH /users/update_password/{id}` | Admin ou o proprio usuario. |
| `PATCH /users/update/{id}` | Apenas `admin`; altera username e `role`. |
| `DELETE /users/delete/{id}` | Admin ou o proprio usuario, respeitando as regras do ultimo admin. |
| `GET /companies` | Disponivel para todos os perfis autenticados. |
| `POST/PATCH/DELETE /companies` | Perfis `admin` e `manager`. |
| Leads, atividades e propostas | `admin` e `manager` acessam de todos; `sales` apenas os proprios. |

## Regras de negocio e validacoes

- Usuario: `username` entre 3 e 20 caracteres; senha entre 8 e 120 caracteres no cadastro.
- O username e normalizado para lowercase no cadastro.
- CNPJ e validado e mascarado com `validate-docbr`.
- Lead:
  - e-mail unico;
  - telefone entre 9 e 11 caracteres;
  - `estimated_value >= 0`;
  - `company_id` precisa existir, quando informado.
- Atividade: `description` entre 3 e 500 caracteres.
- Proposta: `value >= 0`, com ate duas casas decimais.
- Empresa:
  - CNPJ unico;
  - nao pode ser excluida enquanto houver leads ativos vinculados.
- Exclusoes:
  - usuarios: soft delete (`is_active = false`), preservando leads, propostas e atividades;
  - leads, empresas, atividades e propostas: exclusao fisica.

## Seguranca da API

- JWT `HS256`, expiracao padrao de 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Tokens incluem `jti`, `iat` e `ver` (a versao do token do usuario).
- O middleware de seguranca adiciona os headers:
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: no-referrer`
- CORS aceita apenas `GET`, `POST`, `PATCH` e `DELETE`, com os headers `Authorization` e `Content-Type`.
- Erros padronizados:

| Status | Significado |
| --- | --- |
| 400 | Regra de negocio ou conflito de integridade. |
| 401 | Credenciais ou token invalidos. |
| 403 | Permissao insuficiente para a acao. |
| 404 | Recurso nao encontrado. |
| 409 | Item ja existente. |
| 429 | Limite de tentativas de login excedido. |

## Frontend

A interface (em `frontend/`) é uma SPA em React 19, TypeScript e Vite, com estilização em Tailwind CSS e formulários validados via Zod (React Hook Form).

### Estrutura

```text
frontend/src/
  components/  Componentes reutilizaveis e modais (empresas, leads, usuarios, layout)
  contexts/    Estado de autenticacao e useAuth()
  pages/       Telas principais (login, dashboard, leads, empresas, configuracao)
  schemas/     Validacoes de formularios
  services/    Cliente HTTP e contratos da API
```

### Navegacao e telas

A navegacao e controlada por estado local em `App.tsx` (`dashboard`, `empresas`, `leads`, `config`).
O pacote `react-router-dom` esta instalado, mas nao e utilizado atualmente.

| Tela | Responsabilidade |
| --- | --- |
| `LoginPage` | Autenticacao. |
| `DashboardPage` | 3 leads recentes, 4 empresas vinculadas e abertura do detalhe do lead. |
| `LeadsPage` | Busca por nome/e-mail/telefone, filtro por status, ordenacao por data, criacao de lead e modal de detalhe. |
| `CompaniesPage` | Visualizacao de empresas para perfis nao-admin (somente leitura). |
| `AdminCompaniesPage` | CRUD de empresas com paginacao, exclusiva para `admin`. |
| `ConfigPage` | Edicao do proprio perfil, troca de senha e gestao de usuarios para `admin`. |

O modal de lead (`LeadDetailModal`) concentra a edicao e exclusao do lead, bem como a criacao,
edicao e exclusao de atividades e propostas.

### Scripts

| Comando | Descricao |
| --- | --- |
| `npm run dev` | Inicia o servidor de desenvolvimento (Vite). |
| `npm run build` | Executa a verificacao de tipos (`tsc -b`) e gera a versao de producao. |
| `npm run lint` | Executa a analise estatica com ESLint. |
| `npm run preview` | Publica localmente o build gerado. |

### Integracao com a API

As chamadas ficam centralizadas em `frontend/src/services/`. O cliente adiciona automaticamente o
cabecalho `Authorization: Bearer <token>` quando ha uma sessao ativa. Caso a API responda `401`, a
sessao local e removida e a aplicacao retorna ao login.

> O React Query (`@tanstack/react-query`) esta instalado e o `QueryClientProvider` esta configurado
> em `frontend/src/main.tsx`, mas as telas atuais ainda fazem data fetching com `axios` + `useEffect`.
> O React Query ainda nao e usado de forma efetiva.

## Testes

Com o ambiente virtual ativo, execute:

```powershell
pytest
```

Para executar com saida detalhada ou filtrar por categoria:

```powershell
# Execucao detalhada
pytest -v

# Apenas testes de servicos
pytest tests/service_tests/

# Apenas testes HTTP
pytest tests/http_tests/
```

Os testes utilizam banco SQLite em memoria isolado para execucao rapida e sem efeitos colaterais. Atualmente, a suite conta com **147 testes automatizados**, distribuidos em:

- **Testes de Servicos (`tests/service_tests/` - 80 testes)**:
  - `test_activity_service.py` (13 testes): criacao, listagem por lead, atualizacao, remocao e validacao de permissoes.
  - `test_auth_service.py` (8 testes): registro, normalizacao de username, autenticacao e validacao de credenciais.
  - `test_companies_service.py` (14 testes): cadastro com controle de perfil, listagem, atualizacao parcial, remocao e unicidade de CNPJ.
  - `test_leads_service.py` (16 testes): criacao, controle de visibilidade por perfil (`sales`, `admin`, `manager`), edicao e remocao.
  - `test_proposal_service.py` (13 testes): criacao, vinculo com leads, consulta, atualizacao e controle de acesso.
  - `test_user_service.py` (16 testes): alteracao de username, troca de senha, autorizacao, bloqueio de degradacao de perfil e exclusao (soft delete).

- **Testes HTTP (`tests/http_tests/` - 63 testes)**:
  - `test_activities_http.py` (9 testes): endpoints de criacao, consulta por lead, atualizacao e delecao de atividades.
  - `test_auth_http.py` (3 testes, novo): rota de login com validacao de credenciais, token e resposta de erro.
  - `test_companies_http.py` (18 testes): rotas de empresas, validacao de CNPJ e restricao para perfil `sales`.
  - `test_leads_http.py` (17 testes): rotas de criacao, listagem com filtros de permissao, atualizacao e remocao de leads.
  - `test_proposals_http.py` (8 testes): rotas de propostas, validacao de vinculo com lead e permissoes.
  - `test_users_http.py` (8 testes): rotas de alteracao de username e senha com validacao de token e usuario autenticado.

- **Testes de Integracao (`tests/integration_tests/` - 4 testes)** (novo):
  - `test_fk_keys.py` (4 testes): integridade referencial com banco real — garante que os bancos respeitem as chaves estrangeiras (PostgreSQL no CI, ou SQLite em memoria com FK habilitada). Marcados com `@pytest.mark.integration`.

Os testes de servicos e HTTP rodam em SQLite em memoria; a marca `integration` exige PostgreSQL real ou SQLite com `PRAGMA foreign_keys=ON`, e usa a variavel `TEST_DATABASE_URL`.

### Como os testes rodam

- `tests/conftest.py` define `SECRET_KEY` e `DEBUG` para a suite.
- Por padrao, usa SQLite em memoria.
- No SQLite, `PRAGMA foreign_keys=ON` e habilitado para validar chaves estrangeiras.
- Com `TEST_DATABASE_URL` apontando para PostgreSQL, a suite usa o banco real.
- Os testes marcados com `@pytest.mark.integration` sao os que exigem integridade referencial real.

Para executar apenas a suite de integracao:

```powershell
pytest tests/integration_tests/
```

## CI / Integracao continua

O projeto usa **GitHub Actions** (`.github/workflows/ci.yml`) como pipeline. O workflow dispara a cada
`push` na `main` e em `pull_request`, com tres jobs:

| Job | Responsabilidade |
| --- | --- |
| `backend` | Lint com ruff e execucao da suite `pytest` sobre banco SQLite (`sqlite:///./ci.db`). |
| `postgres` | Suite de integracao (`tests/integration_tests`) contra PostgreSQL 16 real, via `TEST_DATABASE_URL`. |
| `frontend` | Lint (ESLint) e build (Vite) da interface em `frontend/`. |

Ambos os jobs de backend rodam com `SECRET_KEY` de teste (nao-relevante para producao) e Python 3.13.
O job `postgres` sobe um container `postgres:16` como servico, cria o banco `crm_test` e expoe a
porta `5432` para a suite de integracao.

O job de lint do backend executa `ruff` apenas nos caminhos `app/main.py`, `app/core/config.py`,
`alembic/env.py`, `tests/conftest.py` e `tests/integration_tests`.

## Comandos uteis

```powershell
# Criar uma nova migracao a partir dos modelos
alembic revision --autogenerate -m "descricao da alteracao"

# Aplicar migracoes pendentes
alembic upgrade head

# Validar o frontend
Set-Location frontend
npm run lint
npm run build
```

## Deploy

O deploy é **local**: o backend roda nativamente com `uvicorn` e o frontend com `vite`;
`docker compose` sobe apenas o PostgreSQL (ver execução acima). Decisão registrada em
docs/adr/ADR-001-deploy-local.md. O frontend consome a API conforme `VITE_API_URL`
(`frontend/.env`) e as origens permitidas no backend são controladas por `CORS_ORIGINS`
(no `.env` raiz), separadas por vírgula.

## Seguranca

- Nunca versione arquivos `.env` ou chaves reais.
- Troque a senha do administrador inicial assim que o primeiro acesso for realizado.
- Gere senhas fortes (por exemplo com um gerenciador de senhas ou `python -c "import secrets; print(secrets.token_urlsafe(16))"`) para `SECRET_KEY`, `ADMIN_PASSWORD` e `POSTGRES_PASSWORD`.
- Use uma `SECRET_KEY` forte em ambientes fora do desenvolvimento.
- O banco configurado pelo Docker e exposto apenas em `127.0.0.1`.
- O login tem limite de 5 tentativas por minuto por combinacao `IP + username`, e falhas sao registradas em log com username e IP (nunca a senha).

## Documentacao relacionada

- `docs/adr/ADR-001-deploy-local.md` — decisao registrada sobre execucao local (backend e frontend nativos, apenas o PostgreSQL em container).
- `.github/workflows/ci.yml` — definicao do pipeline de CI.
