# ADR-001 — Deploy e execução em ambiente local

- **Status:** Aceito (2026-10-29)
- **Contexto associado:** Plano de Correções P3 item 31.

## Contexto

`app/main.py` importava código morto (Alembic, `asyncio`, `time`, path de `alembic.ini`)
com a intenção implícita de rodar migrações dentro da própria app. O
`docker-compose.yml`, porém, só sobe o banco PostgreSQL; backend e frontend rodam
nativamente na máquina do desenvolvedor. Não existem `Dockerfile` nem serviço de app no
compose.

O plano de correções pedia: ou criar `Dockerfile` de backend/frontend para subir a stack
completa, ou **documentar explicitamente que o deploy é local**.

## Decisão

O backend é executado **nativamente** (`uvicorn app.main:app`) e o frontend pelo `vite`,
ambos na máquina do desenvolvedor. `docker compose` é usado **somente** para o PostgreSQL.

- `docker-compose.yml` mantém **apenas o serviço `db`**.
- O backend precisa que o banco esteja saudável antes de subir — o `db` já possui
  `healthcheck`; o operador sobe o banco primeiro (`docker compose up -d db`) e só então
  inicia a API, conforme o `README.md` (seção "Execução local").
- Migrações Alembic rodam na CLI (`alembic upgrade head`), não no startup da app. O
  `main.py` não deve embutir execução de migração.

## Consequências

- **Positivas:** setup simples e rápido para desenvolvimento; nenhuma camada extra
  (contêiner de app) para depurar; alinhado ao uso atual do projeto.
- **Negativas:** para publicar em servidor, será preciso decidir o empacotamento
  (ex.: `Dockerfile` de uvicorn + nginx para o build estático do `vite`). Isso é
  conhecimento futuro — quando houver necessidade de deploy remoto, este ADR deve ser
  revisitado e a stack de contêineres especificada.

## Alternativas consideradas

- **Subir app + frontend em contêineres com `docker compose`:** rejeitado por hora —
  adiciona complexidade de build (multi-stage, nginx, volumes) sem demanda atual. Pode
  ser o caminho quando existir um ambiente de homologação/produção.