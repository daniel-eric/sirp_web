# SIRP — System Integration Ruralinda Problems

Plataforma web de rede social acadêmica para conectar estudantes de diferentes cursos e instituições, permitindo a publicação de problemas técnicos e científicos como vitrine para recrutamento de colaboradores multidisciplinares.

Inicialmente focada na **Universidade Federal Rural de Pernambuco (UFRPE)**, a plataforma está em expansão para integrar discentes de outras instituições de ensino, fortalecendo o ecossistema de inovação por meio da cooperação transversal entre diferentes campos do saber.

## Arquitetura

```
sirp_web/
├── home.py                      # Entry point — aplicação FastAPI
├── requirements.txt             # Dependências Python
├── .env                         # GOOGLE_API_KEY
├── sirp.db                      # Banco SQLite (gerado automaticamente)
│
├── backend/
│   ├── dependencies.py          # Singletons compartilhados (templates, db, repos, sessões)
│   ├── bot_core.py              # Máquina de estados do chatbot + integração Gemini
│   └── chatbot_service.py       # Gerenciador de sessões do chatbot por usuário
│
├── database/
│   ├── db_config.py             # Conexão SQLite + inicialização das tabelas
│   ├── users.py                 # Modelo User + UserRepository (CRUD)
│   └── desafios.py              # Modelo Desafio + DesafioRepository (CRUD, busca, BLOB)
│
├── routes/
│   ├── auth.py                  # POST /login e POST /sign-up
│   ├── paginas.py               # GETs de páginas (index, perfil, reportar)
│   ├── perfil.py                # Atualização e exclusão de perfil
│   ├── desafios.py              # CRUD de desafios + GET /api/desafios/{id}/imagem
│   ├── chat.py                  # API do chatbot (/api/chat, /api/reset, /api/chat/state, /api/chat/cancel)
│   └── media.py                 # Upload de imagens com compressão WebP
│
├── frontend/
│   ├── index.html               # Feed de problemas com cards-pasta + polaroid
│   ├── login.html               # Página de login
│   ├── cadastro.html            # Página de cadastro
│   ├── perfil.html              # Perfil do usuário com edição inline
│   ├── reportar.html            # Criação de problema via chatbot obrigatório
│   ├── css/
│   │   ├── base.css             # Design system (variáveis, layout, header, footer)
│   │   ├── index.css            # Feed (busca, filtros, folder, polaroid, FAB)
│   │   ├── perfil.css           # Cards de credenciais, formulários de edição
│   │   └── reportar.css         # Chat wrapper, mensagens, modal de upload
│   ├── js/
│   │   ├── shared.js            # Menu hamburguer, toggle senha, logout
│   │   ├── index.js             # Filtros avançados, abrir/fechar pastas
│   │   ├── login.js             # Popup "Esqueci a senha"
│   │   ├── perfil.js            # Edição inline, confirmação de exclusão
│   │   └── reportar.js          # Widget de chat inline
│   └── assets/                  # Imagens e recursos visuais
│
├── uploads/                     # Imagens enviadas pelos usuários (WebP)
└── .gitignore
```

## Stack Tecnológica

| Camada         | Tecnologia                            |
|----------------|---------------------------------------|
| **Runtime**    | Python 3.12                           |
| **Framework**  | FastAPI 0.136.3 (ASGI)                |
| **Templates**  | Jinja2 (via `fastapi.templating`)     |
| **Banco**      | SQLite 3 (via `sqlite3` stdlib)       |
| **IA**         | Google Gemini 2.5 Flash (JSON mode)   |
| **Imagens**    | Pillow 10+ (compressão WebP quality 65)|
| **Frontend**   | HTML5 + CSS3 + SVG + JS vanilla       |
| **Servidor**   | Uvicorn                               |
| **Auth**       | Cookie HTTP-only (`logged_user`)      |

## Funcionalidades

### Usuários
- Cadastro e autenticação por email/username e senha
- Atualização de nome de usuário, senha e telefone
- Exclusão de conta

### Desafios (Problemas)
- Criação assistida por chatbot com IA (Gemini 2.5 Flash) — formulário manual substituído
- Fluxo em etapas: coleta inicial → investigação estruturada → confirmação com edição
- Upload de imagem ao final do chat, com compressão automática para WebP
- Imagem armazenada como BLOB no banco e exibida como polaroid no feed
- Busca e filtragem por título, áreas, autor e data
- Edição inline de atributos e exclusão
- Feed público com cards estilo pasta + polaroid

### Chatbot
- Máquina de estados (`EstadoColetaInicial` → `EstadoInvestigacao` → `EstadoConfirmacao`)
- Respostas em JSON mode com esquema validado
- System instruction com proteção anti-injeção e controle de falsos positivos
- Sessão por usuário em memória com suporte a reset e cancelamento

### Validação
- Domínio de email restrito a `@ufrpe.br`
- Validação de username, telefone e senha

## Banco de Dados

### `users`

| Coluna   | Tipo    | Restrições              |
|----------|---------|--------------------------|
| id       | INTEGER | PRIMARY KEY AUTOINCREMENT|
| username | TEXT    | NOT NULL                 |
| email    | TEXT    | UNIQUE, NOT NULL         |
| password | TEXT    | NOT NULL                 |
| tellNum  | TEXT    | —                        |

### `desafios`

| Coluna           | Tipo      | Restrições              |
|------------------|-----------|--------------------------|
| id               | INTEGER   | PRIMARY KEY AUTOINCREMENT|
| titulo           | TEXT      | NOT NULL                 |
| autor            | TEXT      | NOT NULL                 |
| contato          | TEXT      | —                        |
| areas            | TEXT      | NOT NULL                 |
| contexto         | TEXT      | —                        |
| atores           | TEXT      | —                        |
| impacto          | TEXT      | —                        |
| contornos        | TEXT      | —                        |
| metricas_sucesso | TEXT      | —                        |
| restricoes       | TEXT      | —                        |
| data_criacao     | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP|
| midia_blob       | BLOB      | —                        |

## Rotas da API

### GET (Páginas)
| Rota               | Autenticação | Descrição                    |
|--------------------|--------------|------------------------------|
| `/`                | —            | Página de login              |
| `/sign-up`         | —            | Página de cadastro           |
| `/landing-page`    | Obrigatória  | Feed de problemas + busca    |
| `/profile`         | Obrigatória  | Perfil do usuário            |
| `/problems-manager`| Obrigatória  | Criar problema via chatbot   |

### POST (Ações)
| Rota                               | Autenticação | Descrição                          |
|-----------------------------------|--------------|--------------------------------------|
| `/login`                           | —            | Autenticar usuário                   |
| `/sign-up`                         | —            | Registrar novo usuário               |
| `/api/profile/update-username`     | Obrigatória  | Atualizar nome de usuário            |
| `/api/profile/update-password`     | Obrigatória  | Atualizar senha                      |
| `/api/profile/update-tellNum`      | Obrigatória  | Atualizar telefone                   |
| `/api/profile/delete-account`      | Obrigatória  | Excluir conta                        |
| `/api/desafios/add`                | Obrigatória  | Criar desafio (fallback)             |
| `/api/desafios/update`             | Obrigatória  | Atualizar atributo do desafio        |
| `/api/desafios/delete`             | Obrigatória  | Excluir desafio                      |
| `/api/chat`                        | Obrigatória  | Enviar mensagem ao chatbot           |
| `/api/reset`                       | Obrigatória  | Reiniciar sessão do chatbot          |
| `/api/chat/cancel`                 | Obrigatória  | Cancelar sessão do chatbot           |
| `/api/upload`                      | Obrigatória  | Upload de imagem (compressão WebP)   |
| `/api/upload_final`                | Obrigatória  | Upload final + vincular BLOB ao desafio|

### GET (Dados)
| Rota                               | Autenticação | Descrição                          |
|-----------------------------------|--------------|--------------------------------------|
| `/api/chat/state`                  | Obrigatória  | Estado atual da sessão do chatbot    |
| `/api/desafios/{id}/imagem`        | —            | Servir imagem BLOB do desafio        |

## Setup e Execução

```bash
# 1. Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar chave da API Gemini
echo "GOOGLE_API_KEY=sua_chave_aqui" > .env

# 4. Iniciar servidor
uvicorn home:app --reload
```

O servidor será iniciado em `http://localhost:8000`. As tabelas do banco são criadas automaticamente na primeira execução.

## Dependências

- `fastapi==0.136.3` — Framework ASGI (inclui Jinja2, Uvicorn e Pydantic)
- `google-genai>=1.0.0` — SDK Google Gemini AI
- `python-dotenv>=1.0.0` — Carregamento de variáveis de ambiente
- `python-multipart>=0.0.9` — Parsing de formulários multipart (uploads)
- `Pillow>=10.0.0` — Compressão de imagens para WebP
