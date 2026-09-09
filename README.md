# CRM de Vendas

Aplicacao web para gerenciamento de leads, empresas, propostas, atividades comerciais e usuarios. O projeto possui uma API REST em FastAPI, interface em React e persistencia em PostgreSQL.

## Funcionalidades

- Autenticacao com JWT e limite de tentativas no login.
- Controle de usuarios com os perfis `admin`, `manager` e `sales`.
- Cadastro, consulta, atualizacao e remocao de empresas e leads.
- Acompanhamento de atividades por lead: ligacao, reuniao, e-mail, WhatsApp e outros.
- Cadastro e acompanhamento de propostas comerciais.
- Dashboard para visualizacao dos leads e empresas recentes.
- Regras de permissao para restringir a gestao de recursos conforme o perfil do usuario.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic |
| Banco de dados | PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, React Query |
| Testes | Pytest |
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

O script cria, quando inexistente, o usuario `admin` com a senha `admin123`. Altere essa senha antes de usar o sistema em qualquer ambiente compartilhado.

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

Todas as rotas da aplicacao usam o prefixo `/api/v1`. Com excecao de registro e login, as rotas exigem o cabecalho `Authorization: Bearer <token>`.

| Modulo | Base da rota | Responsabilidade |
| --- | --- | --- |
| Autenticacao | `/auth` | Registro, login e token JWT |
| Usuarios | `/users` | Perfil, listagem e administracao de usuarios |
| Leads | `/leads` | Gestao e consulta paginada de leads |
| Empresas | `/companies` | Gestao de empresas por CNPJ |
| Atividades | `/activities` | Historico comercial vinculado a leads |
| Propostas | `/proposals` | Propostas vinculadas a leads |

Principais estados aceitos:

- Leads: `new`, `contacted`, `lost`, `won`.
- Propostas: `pending`, `accepted`, `rejected`.
- Atividades: `call`, `meeting`, `email`, `whatsapp`, `other`.

## Testes

Com o ambiente virtual ativo, execute:

```powershell
pytest
```

Os testes cobrem a camada de servicos e os endpoints HTTP, utilizando banco SQLite em memoria para o ambiente de teste.

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

## Seguranca

- Nunca versione arquivos `.env` ou chaves reais.
- Troque a senha do administrador inicial assim que o primeiro acesso for realizado.
- Use uma `SECRET_KEY` forte em ambientes fora do desenvolvimento.
- O banco configurado pelo Docker e exposto apenas em `127.0.0.1`.
