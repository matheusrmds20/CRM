# Frontend — CRM de Vendas

Interface web do CRM de Vendas, desenvolvida em React, TypeScript e Vite. A aplicacao permite autenticar usuarios, acompanhar leads, empresas, atividades e propostas, alem de administrar usuarios conforme o perfil de acesso.

## Tecnologias

- React 19 e TypeScript
- Vite
- Axios
- React Hook Form e Zod
- Tailwind CSS
- ESLint

## Pre-requisitos

- Node.js 20 ou superior
- API do CRM em execucao (por padrao, em `http://localhost:8000`)

## Configuracao

Instale as dependencias:

```powershell
npm install
```

Por padrao, o cliente HTTP usa `http://localhost:8000/api/v1`. Para usar outra instancia, crie um arquivo `.env` nesta pasta:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Execucao

```powershell
npm run dev
```

O Vite exibira a URL local da interface, normalmente `http://localhost:5173`.

## Scripts

| Comando | Descricao |
| --- | --- |
| `npm run dev` | Inicia o servidor de desenvolvimento. |
| `npm run build` | Executa a verificacao de tipos e gera a versao de producao. |
| `npm run lint` | Executa a analise estatica com ESLint. |
| `npm run preview` | Publica localmente o build gerado. |

## Funcionalidades

- Login com token JWT persistido localmente.
- Dashboard com leads e empresas.
- Criacao, edicao e remocao de leads.
- Criacao, edicao e remocao de empresas para administradores.
- Registro, edicao e remocao de atividades e propostas em cada lead.
- Administracao de usuarios na pagina de configuracoes, conforme as permissoes da conta.

## Estrutura

```text
src/
  components/  Componentes reutilizaveis e modais
  contexts/    Estado de autenticacao
  pages/       Telas principais da aplicacao
  schemas/     Validacoes de formularios
  services/    Cliente HTTP e contratos da API
```

## Integracao com a API

As chamadas ficam centralizadas em `src/services/`. O cliente adiciona automaticamente o cabecalho `Authorization: Bearer <token>` quando ha uma sessao ativa. Caso a API responda `401`, a sessao local e removida e a aplicacao retorna ao login.
