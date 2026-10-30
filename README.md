# CRM de Vendas

Aplicacao web para gerenciamento de leads, empresas, propostas, atividades comerciais e usuarios. O projeto possui uma API REST em FastAPI, interface em React e persistencia em PostgreSQL.

## Funcionalidades

- Autenticacao com JWT e limite de tentativas no login (5 por minuto, por IP e por usuario).
- Invalidação de tokens antigos ao alterar username ou senha (via token version).
- Controle de usuarios com os perfis `admin`, `manager` e `sales`.
- Cadastro, listagem, atualizacao e remocao de empresas e leads.
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
| Gerenciar usuarios (role, username, senha) | sim | nao | nao |

A implementacao vive em `app/utils/permissions.py`. Apenas um admin pode alterar perfis;
nenhum admin pode rebaixar o proprio perfil, se auto-excluir ou deixar o sistema sem um
administrador ativo (a exclusao de usuario e um soft delete: o usuario fica inativo e seus
leads, propostas e atividades sao preservados).

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, slowapi (rate limiting) |
| Banco de dados | PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, React Query |
| Testes | Pytest, GitHub Actions (CI) |
| Infraestrutura local | Docker Compose |

## Estrutura

```text
app/                 API FastAPI
  api/               Rotas e dependencias
  core/              Configuracao e seguranca
  db/                Conexao e base do SQLAlchemy
  models/            Modelos ORM
  repositories/      Acesso a dados
  schemas/           Contratos Pydantic
  services/          Regras de negocio
alembic/             Migracoes do banco de dados
db/init/             Inicializacao do PostgreSQL no Docker
frontend/            Aplicacao React
tests/               Testes de servico e HTTP
```

## Pre-requisitos

- Python 3.12 ou superior
- Node.js 20 ou superior
- Docker Desktop com Docker Compose

## Configuracao

Crie um arquivo `.env` na raiz do projeto. A aplicacao espera as variaveis abaixo:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/CRM
SECRET_KEY=troque-por-uma-chave-secreta-com-pelo-menos-32-caracteres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
# Origens CORS permitidas, separadas por vírgula (sem path na URL).
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`SECRET_KEY` deve ser exclusiva e mantida fora do controle de versao. O arquivo `.env` ja esta ignorado pelo Git.

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

Todas as rotas da aplicacao usam o prefixo `/api/v1`. Com excecao de `POST /auth/login`, as rotas exigem o cabecalho `Authorization: Bearer <token>`.

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

## Frontend

A interface (em `frontend/`) é uma SPA em React 19, TypeScript e Vite, com estilização em Tailwind CSS e formulários validados via Zod (React Hook Form).

### Estrutura

```text
frontend/src/
  components/  Componentes reutilizaveis e modais
  contexts/    Estado de autenticacao e useAuth()
  pages/       Telas principais (login, dashboard, leads, empresas, configuracao)
  schemas/     Validacoes de formularios
  services/    Cliente HTTP e contratos da API
```

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
