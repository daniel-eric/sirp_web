# SIRP — System Integration Ruralinda Problems

Plataforma web de rede social acadêmica para conectar estudantes de diferentes cursos e instituições, permitindo a publicação de problemas técnicos e científicos como vitrine para recrutamento de colaboradores multidisciplinares.

Inicialmente focada na **Universidade Federal Rural de Pernambuco (UFRPE)**, a plataforma está em expansão para integrar discentes de outras instituições de ensino, fortalecendo o ecossistema de inovação por meio da cooperação transversal entre diferentes campos do saber.

## Stack Tecnológica

| Camada            | Tecnologia                                        |
|-------------------|---------------------------------------------------|
| **Runtime**       | Python 3.12+                                      |
| **Framework**     | FastAPI 0.136.3 (ASGI)                            |
| **Templates**     | Jinja2 (via `fastapi.templating`)                 |
| **Banco**         | SQLite 3 (via `sqlite3` stdlib)                   |
| **IA**            | Google Gemini 2.5 Flash (JSON mode)               |
| **Imagens**       | Pillow 10+ (compressão WebP quality 65)           |
| **Vídeo**         | ffmpeg (H.264 libx264, CRF 28, max 854x480, 30s) |
| **Criptografia**  | Fernet (symmetric, chats)                         |
| **Email**         | smtplib + Gmail SMTP (App Password)               |
| **Frontend**      | HTML5 + CSS3 + SVG + JavaScript vanilla           |
| **Servidor**      | Uvicorn                                           |
| **Auth**          | Cookie HTTP-only (`logged_user` com email plano)  |

## Arquitetura

```
sirp_web/
├── home.py                      # Entry point — aplicação FastAPI + load_dotenv()
├── requirements.txt             # Dependências Python
├── .env                         # GOOGLE_API_KEY, GEMINI_API_KEY[1-9], GMAIL_*, CHAT_ENCRYPTION_KEY
├── sirp.db                      # Banco SQLite (gerado automaticamente na 1ª execução)
│
├── backend/                     # Camada de serviços / lógica de negócio
│   ├── dependencies.py          # Singletons compartilhados (templates, db, repos, sessões, crypto)
│   ├── bot_core.py              # Máquina de estados do chatbot + integração Gemini + key rotation
│   ├── chatbot_service.py       # Gerenciador de sessões por usuário (dict em memória)
│   ├── crypto_utils.py          # Criptografia Fernet para mensagens de chat
│   └── email_service.py         # Envio de email via Gmail SMTP (recuperação de senha)
│
├── database/                    # Camada de acesso a dados (Repository Pattern)
│   ├── db_config.py             # DatabaseManager (singleton), DatabaseConnection (context manager), init + migrations
│   ├── users.py                 # Modelo User (dataclass) + UserRepository (CRUD)
│   ├── desafios.py              # Modelo Desafio (dataclass) + DesafioRepository (CRUD, busca LIKE, BLOB)
│   └── chat_db.py               # ChatRepository (CRUD conversas, participantes, mensagens criptografadas)
│
├── routes/                      # Camada de controllers (handlers HTTP)
│   ├── paginas.py               # GETs de páginas (login, sign-up, landing-page, profile, problems-manager)
│   ├── auth.py                  # POST /login, /sign-up, /api/forgot-password
│   ├── perfil.py                # POSTs de atualização e exclusão de perfil
│   ├── desafios.py              # CRUD de desafios + compartilhar via DM + servir imagem/vídeo
│   ├── chat.py                  # API do chatbot (/api/chat, /api/reset, /api/chat/state, /api/chat/cancel)
│   ├── chat_grupo.py            # API de chat em grupo/DM (criar, mensagens, convidar, bloquear)
│   └── media.py                 # Upload + compressão de imagem (WebP) e vídeo (ffmpeg)
│
├── frontend/                    # Interface SPA-like (server-rendered + JS vanilla)
│   ├── index.html               # Feed de problemas com cards-pasta + polaroid + busca/filtro
│   ├── login.html               # Página de login com popup "Esqueci a senha"
│   ├── cadastro.html            # Página de cadastro
│   ├── perfil.html              # Perfil do usuário com edição inline
│   ├── reportar.html            # Criação de problema via chatbot (obrigatório)
│   ├── chat.html                # Interface de chat em grupo/DM com sidebar
│   ├── css/
│   │   ├── base.css             # Design system (variáveis CSS, reset, layout, header, footer)
│   │   ├── index.css            # Feed (busca, filtros, folder-card, polaroid, FAB)
│   │   ├── perfil.css           # Cards de credenciais, formulários de edição
│   │   ├── reportar.css         # Chat wrapper, mensagens, modal de upload
│   │   └── chat.css             # Sidebar de conversas, balões de mensagem, status
│   ├── js/
│   │   ├── shared.js            # Menu hambúrguer, toggle senha, logout
│   │   ├── index.js             # Filtros avançados, abrir/fechar pastas, compartilhar
│   │   ├── login.js             # Popup "Esqueci a senha" (fetch /api/forgot-password)
│   │   ├── perfil.js            # Edição inline, confirmação de exclusão
│   │   ├── reportar.js          # Widget de chat inline com polling de estado
│   │   ├── chat.js              # Cliente de chat completo (polling 4s, enviar, bloquear/desbloquear)
│   │   └── cadastro.js          # (placeholder)
│   └── assets/                  # Imagens e recursos visuais
│
├── uploads/                     # Mídias enviadas pelos usuários
│   └── videos/                  # Vídeos processados (H.264, max 30s)
└── .gitignore
```

### Padrões de Design

| Padrão            | Onde                                     | Descrição |
|-------------------|------------------------------------------|-----------|
| **Repository**    | `database/users.py`, `desafios.py`, `chat_db.py` | Abstração de acesso a dados com injeção de `DatabaseManager` |
| **State**         | `backend/bot_core.py`                    | `EstadoBot` → `EstadoColetaInicial` → `EstadoInvestigacao` → `EstadoConfirmacao` |
| **Singleton**     | `backend/dependencies.py`                | Instâncias únicas de `DatabaseManager`, repositórios, `ChatbotSessionManager`, `CryptoUtils` |
| **Context Manager** | `database/db_config.py`                | `DatabaseConnection` com `__enter__`/`__exit__` para cleanup automático |
| **Dataclass**     | `database/users.py`, `desafios.py`       | Modelos `User` e `Desafio` como dataclasses Python |

## Funcionalidades

### Usuários
- Cadastro e autenticação por email/username + senha (cookie HTTP-only `logged_user`)
- Atualização de nome de usuário, senha e telefone
- Recuperação de senha via email (token aleatório, enviado em plaintext via Gmail SMTP)
- Exclusão de conta

### Desafios (Problemas)
- Criação assistida obrigatória por chatbot com IA (Gemini 2.5 Flash) — sem formulário manual
- Fluxo em etapas: coleta inicial → investigação estruturada → confirmação com edição
- Upload de imagem ao final do chat, com compressão automática para WebP (Pillow, quality 65)
- Upload de vídeo com processamento ffmpeg (trim 30s, H.264 CRF 28, max 854x480, AAC 128k)
- Imagem armazenada como BLOB no banco e/ou em disco; vídeo em `uploads/videos/`
- Busca e filtragem por título, áreas, autor e data (SQL `LIKE`)
- Edição inline de atributos e exclusão
- Feed público com cards no estilo pasta + polaroid (CSS clip-path animation)
- Compartilhar problema via DM (cria/conversa DM e envia mensagem formatada)

### Chatbot (IA)
- Máquina de estados: `EstadoColetaInicial` → `EstadoInvestigacao` → `EstadoConfirmacao`
- Respostas em JSON mode com esquema validado (`response_mime_type: application/json`)
- System instruction com proteção anti-injeção e controle de falsos positivos
- Sessão por usuário em memória (dict), com suporte a reset e cancelamento
- **Key rotation automática**: até 9 chaves Gemini (`GEMINI_API_KEY1`-`GEMINI_API_KEY9`) com fallback em `429`/`RESOURCE_EXHAUSTED`
- Validação de input: max 3000 caracteres, min 15 no estado inicial, detecção de saudações

### Chat em Grupo / DM
- Conversas de grupo e direct messages com participantes
- Mensagens criptografadas com **Fernet** (symmetric key via `CHAT_ENCRYPTION_KEY`)
- Polling a cada 4 segundos para novas mensagens (sem WebSocket)
- Bloqueio/desbloqueio de conversas por usuário
- Criação de DM automática ao compartilhar problema

### Validação
- Domínio de email restrito a `@ufrpe.br` (validação apenas no frontend)
- Validação de username, telefone (11-13 dígitos) e senha (min 8 caracteres)

## Banco de Dados

### `users`
| Coluna    | Tipo    | Restrições               |
|-----------|---------|--------------------------|
| id        | INTEGER | PRIMARY KEY AUTOINCREMENT|
| username  | TEXT    | NOT NULL, UNIQUE         |
| email     | TEXT    | UNIQUE, NOT NULL         |
| password  | TEXT    | NOT NULL (plaintext)     |
| tellNum   | TEXT    | —                        |

### `desafios`
| Coluna           | Tipo      | Restrições               |
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
| video_path       | TEXT      | — (adicionado via migration) |

### `conversas`
| Coluna        | Tipo      | Restrições               |
|---------------|-----------|--------------------------|
| id            | INTEGER   | PRIMARY KEY AUTOINCREMENT|
| nome          | TEXT      | NOT NULL                 |
| tipo          | TEXT      | NOT NULL DEFAULT 'group' |
| data_criacao  | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP|
| bloqueado_por | TEXT      | — (adicionado via migration) |

### `participantes`
| Coluna      | Tipo    | Restrições                    |
|-------------|---------|-------------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT     |
| conversa_id | INTEGER | NOT NULL, FK → conversas(id)  |
| user_email  | TEXT    | NOT NULL, UNIQUE(conversa_id, user_email) |

### `mensagens`
| Coluna      | Tipo      | Restrições               |
|-------------|-----------|--------------------------|
| id          | INTEGER   | PRIMARY KEY AUTOINCREMENT|
| conversa_id | INTEGER   | NOT NULL, FK → conversas(id) |
| autor_email | TEXT      | NOT NULL                 |
| conteudo    | TEXT      | NOT NULL (Fernet-encrypted) |
| data_envio  | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP|

### `bloqueios`
| Coluna       | Tipo      | Restrições               |
|--------------|-----------|--------------------------|
| id           | INTEGER   | PRIMARY KEY AUTOINCREMENT|
| conversa_id  | INTEGER   | NOT NULL, FK → conversas(id) |
| user_email   | TEXT      | NOT NULL                 |
| data_bloqueio| TIMESTAMP | DEFAULT CURRENT_TIMESTAMP|

### Migrations (inline em `db_config.py`)
- `db_bloqueio_migration()`: adiciona coluna `bloqueado_por` em `conversas` e migra dados de `bloqueios`
- `db_video_migration()`: adiciona coluna `video_path` em `desafios`
- Executadas em `try`/`except` para idempotência

## Rotas da API

### GET (Páginas)
| Rota                | Autenticação | Descrição                         |
|---------------------|--------------|-----------------------------------|
| `/`                 | —            | Página de login                   |
| `/sign-up`          | —            | Página de cadastro                |
| `/landing-page`     | Obrigatória  | Feed de problemas + busca/filtro  |
| `/profile`          | Obrigatória  | Perfil do usuário                 |
| `/problems-manager` | Obrigatória  | Criar problema via chatbot        |
| `/chat`             | Obrigatória  | Interface de chat em grupo/DM     |

### POST (Autenticação e Perfil)
| Rota                               | Autenticação | Descrição                        |
|------------------------------------|--------------|----------------------------------|
| `/login`                           | —            | Autenticar, setar cookie         |
| `/sign-up`                         | —            | Registrar novo usuário           |
| `/api/forgot-password`             | —            | Enviar email de recuperação      |
| `/api/profile/update-username`     | Obrigatória  | Atualizar nome de usuário        |
| `/api/profile/update-password`     | Obrigatória  | Atualizar senha                  |
| `/api/profile/update-tellNum`      | Obrigatória  | Atualizar telefone               |
| `/api/profile/delete-account`      | Obrigatória  | Excluir conta                    |

### POST (Desafios e Chatbot)
| Rota                               | Autenticação | Descrição                            |
|------------------------------------|--------------|--------------------------------------|
| `/api/desafios/add`                | Obrigatória  | Criar desafio (fallback)             |
| `/api/desafios/update`             | Obrigatória  | Atualizar atributo do desafio        |
| `/api/desafios/delete`             | Obrigatória  | Excluir desafio                      |
| `/api/desafios/{id}/compartilhar`  | Obrigatória  | Compartilhar desafio via DM          |
| `/api/chat`                        | Obrigatória  | Enviar mensagem ao chatbot           |
| `/api/reset`                       | Obrigatória  | Reiniciar sessão do chatbot          |
| `/api/chat/cancel`                 | Obrigatória  | Cancelar sessão do chatbot           |

### POST (Chat em Grupo)
| Rota                               | Autenticação | Descrição                            |
|------------------------------------|--------------|--------------------------------------|
| `/api/conversas/criar`             | Obrigatória  | Criar conversa em grupo              |
| `/api/conversas/dm`                | Obrigatória  | Criar/obter conversa DM              |
| `/api/conversas/{id}/mensagens`    | Obrigatória  | Enviar mensagem em conversa          |
| `/api/conversas/{id}/convidar`     | Obrigatória  | Adicionar participante               |
| `/api/conversas/{id}/bloquear`     | Obrigatória  | Bloquear conversa                    |
| `/api/conversas/{id}/desbloquear`  | Obrigatória  | Desbloquear conversa                 |

### POST (Mídia)
| Rota                               | Autenticação | Descrição                            |
|------------------------------------|--------------|--------------------------------------|
| `/api/upload`                      | Obrigatória  | Upload + compressão de imagem (WebP) |
| `/api/upload_final`                | Obrigatória  | Upload final + vincular mídia ao desafio |

### GET (Dados)
| Rota                               | Autenticação | Descrição                            |
|------------------------------------|--------------|--------------------------------------|
| `/api/chat/state`                  | Obrigatória  | Estado atual da sessão do chatbot    |
| `/api/users/search`                | Obrigatória  | Buscar usuários por query            |
| `/api/conversas`                   | Obrigatória  | Listar conversas do usuário          |
| `/api/conversas/{id}/mensagens`    | Obrigatória  | Obter mensagens (polling, suporta `ultimo_id`) |
| `/api/conversas/{id}/bloqueio`     | Obrigatória  | Verificar status de bloqueio         |
| `/api/desafios/{id}/imagem`        | —            | Servir imagem BLOB do desafio        |
| `/api/desafios/{id}/video`         | —            | Servir arquivo de vídeo do desafio   |

## Processamento de Mídia

### Imagens (`routes/media.py`)
- Upload → compressão com Pillow para **WebP quality 65**
- RGBA/LA convertido para RGB antes da compressão
- Armazenado como BLOB no banco + arquivo em `uploads/`
- Servido via `/api/desafios/{id}/imagem`

### Vídeos (`routes/media.py`)
- Requer `ffmpeg` instalado (verificação em `home.py`)
- Pipeline: trim 30s → H.264 CRF 28 → scale max 854x480 → AAC 128k → fast-start
- Armazenado em `uploads/videos/`
- Servido via `/api/desafios/{id}/video`

## Criptografia (Chat)

- Algoritmo: **Fernet** (AES-128-CBC + HMAC-SHA256)
- Chave: `CHAT_ENCRYPTION_KEY` no `.env`
- Mensagens criptografadas em `crypto_utils.py` antes de persistir em `chat_db.py`
- Decriptação no momento da leitura

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
- `cryptography>=41.0.0` — Criptografia Fernet para mensagens de chat
