# SIRP — System Integration Ruralinda Problems

Plataforma web de rede social acadêmica para conectar estudantes de diferentes cursos e instituições, permitindo a publicação de problemas técnicos e científicos como vitrine para recrutamento de colaboradores multidisciplinares.

Inicialmente focada na **Universidade Federal Rural de Pernambuco (UFRPE)**, a plataforma está em expansão para integrar discentes de outras instituições de ensino, fortalecendo o ecossistema de inovação por meio da cooperação transversal entre diferentes campos do saber.

## Arquitetura

```
sirp_web/
├── home.py                      # Entry point — aplicação FastAPI
├── requirements.txt             # Dependências Python
├── sirp.db                      # Banco SQLite (gerado automaticamente)
├── backend/
│   └── validations/
│       └── validacoes.py        # Serviço de validação de entrada
├── database/
│   ├── db_config.py             # Conexão e inicialização do banco
│   ├── users.py                 # Modelo User + UserRepository (CRUD)
│   └── problems.py              # Modelo Problem + ProblemRepository (CRUD + busca)
├── frontend/
│   ├── index.html               # Landing page com cards interativos
│   ├── login.html               # Página de login (estática)
│   ├── cadastro.html            # Página de cadastro (estática)
│   ├── perfil.html              # Página de perfil (estática)
│   ├── reportar.html            # Página de reportar problema (estática)
│   ├── css/
│   │   └── style.css            # Folha de estilos principal
│   └── assets/                  # Imagens e recursos visuais
└── templates/                   # Templates Jinja2 renderizados pelo servidor
    ├── index.html               # Login (POST /login)
    ├── sign_up.html             # Cadastro (POST /sign-up)
    ├── landing_page.html        # Menu pós-login
    ├── profile.html             # Perfil do usuário com edição
    ├── problems_feed.html       # Feed de problemas com busca/filtro
    └── problems_manager.html    # Cadastro de novos problemas
```

## Stack Tecnológica

| Camada        | Tecnologia                      |
|---------------|----------------------------------|
| **Runtime**   | Python 3.12                      |
| **Framework** | FastAPI 0.136.3 (ASGI)           |
| **Templates** | Jinja2 (via `fastapi.templating`)|
| **Banco**     | SQLite 3 (via `sqlite3` stdlib)  |
| **Frontend**  | HTML5 + CSS3 + SVG               |
| **Servidor**  | Uvicorn                           |
| **Auth**      | Cookie HTTP-only (`logged_user`)  |

## Funcionalidades

### Usuários
- Cadastro e autenticação por email/username e senha
- Atualização de nome de usuário, senha e telefone
- Exclusão de conta

### Problemas
- Criação de problemas com título, descrição e áreas de conhecimento
- Busca e filtragem por título, áreas, autor e data
- Atualização dinâmica de atributos e exclusão
- Feed público com cards de problemas

### Validação
- Serviço de validação de entrada (`validacoes.py`) com regras para username, email (domínio @ufrpe.br), telefone e senha

## Banco de Dados

### `users`
| Coluna   | Tipo    | Restrições              |
|----------|---------|--------------------------|
| id       | INTEGER | PRIMARY KEY AUTOINCREMENT|
| username | TEXT    | NOT NULL                 |
| email    | TEXT    | UNIQUE, NOT NULL         |
| password | TEXT    | NOT NULL                 |
| tellNum  | TEXT    | —                        |

### `problems`
| Coluna      | Tipo    | Restrições              |
|-------------|---------|--------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT|
| title       | TEXT    | NOT NULL                 |
| description | TEXT    | NOT NULL                 |
| areas       | TEXT    | NOT NULL                 |
| authors     | TEXT    | NOT NULL                 |
| time        | TEXT    | NOT NULL                 |

## Rotas da API

### GET (Páginas)
| Rota              | Autenticação | Descrição                |
|--------------------|--------------|--------------------------|
| `/`                | —            | Página de login          |
| `/sign-up`         | —            | Página de cadastro       |
| `/landing-page`    | —            | Menu principal           |
| `/profile`         | Obrigatória  | Perfil do usuário        |
| `/problems-feed`   | Obrigatória  | Feed de problemas        |
| `/problems-manager`| Obrigatória  | Gerenciar problemas      |

### POST (Ações)
| Rota                               | Autenticação | Descrição                    |
|-----------------------------------|--------------|------------------------------|
| `/login`                           | —            | Autenticar usuário           |
| `/sign-up`                         | —            | Registrar novo usuário       |
| `/api/profile/update-username`     | Obrigatória  | Atualizar nome de usuário    |
| `/api/profile/update-password`     | Obrigatória  | Atualizar senha              |
| `/api/profile/update-tellNum`      | Obrigatória  | Atualizar telefone           |
| `/api/profile/delete-account`      | Obrigatória  | Excluir conta                |
| `/api/problems/add`                | Obrigatória  | Criar problema               |
| `/api/problems/update`             | Obrigatória  | Atualizar campo do problema  |
| `/api/problems/delete`             | Obrigatória  | Excluir problema             |

## Execução

```bash
uvicorn home:app --reload
```

O servidor será iniciado em `http://localhost:8000`.

## Dependências

- `fastapi>=0.136.3` (inclui Jinja2, Uvicorn e Pydantic como dependências transitivas)
