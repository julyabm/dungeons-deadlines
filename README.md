# Dungeons & Deadlines

Um aplicativo web que combina **gamificação RPG** com **gerenciamento de tarefas**. Transforme seus afazeres em uma aventura épica!

## Tecnologias

- **Backend**: Django 6.0.5
- **Banco de Dados**: PostgreSQL
- **Python**: 3.13+

## Instalação


### 2. Como rodar o projeto?

Existem 2 opções disponíveis para rodar o projeto:

### Opção 1: Rodando com Docker (Recomendado)
Esta opção não exige que você tenha Python ou PostgreSQL instalados fisicamente na sua máquina. Tudo rodará isolado dentro de containers.

#### 1.1 Pré-requisitos
* **Docker** instalado ([Instruções de instalação](https://docs.docker.com/get-docker/))
* **Docker Compose** instalado (já vem embutido no Docker Desktop)

#### 1.2 Inicialização rápida
Na pasta raiz do projeto (onde estão localizados o `Dockerfile` e o `docker-compose.yml`), execute o comando abaixo no seu terminal:

```bash
docker compose up --build
```

#### 1.3 Utilizando a plataforma
Acesse a [aplicação local](https://localhost:8000) e crie um usuário para você, ou utilize o administrador criado por padrão:
```text
email: admin@exemplo.com
senha: admin
```
---
### Opção 2: rodando localmente

#### 2.1 Pré-requisitos

- Python 3.13+
- PostgreSQL instalado e rodando

#### 2.2 Ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/Scripts/activate
```

#### 2.3 Dependências

```bash
pip install -r requirements.txt
```

#### 2.4 Credenciais de uso

Caso opte por rodar a aplicação localmente, renomeie o arquivo `.env.example` para `.env` 
e ajuste as credenciais conforme o desejado. Crie também o banco de dados postgres na sua máquina:

```sql
CREATE DATABASE dungeons_deadlines;
```

#### 2.5 Migrations e dados iniciais

```bash
python manage.py migrate
python manage.py seed_items
python manage.py createsuperuser
```

#### 2.6 Servidor

```bash
python manage.py runserver --insecure
```

Acesse a [aplicação local](https://localhost:8000).

## Rotas da aplicação

| Rota | Descrição |
|------|-----------|
| `/` | Landing page |
| `/cadastro/` | Registro de usuário |
| `/contas/login/` | Login (e-mail) |
| `/dashboard/` | Painel do jogador |
| `/tarefas/` | CRUD de tarefas |
| `/missoes/` | Missões do dia |
| `/loja/` | Loja de itens |
| `/inventario/` | Inventário e equipamentos |
| `/amigos/` | Amigos e ranking |
| `/admin/` | Django Admin (gestão de usuários) |

## Funcionalidades

- **Autenticação** por e-mail e senha (sem OAuth)
- **Avatar RPG**: HP, XP, nível, ouro
- **Tarefas** com dificuldade (Slime/Ogro/Dragão) e recompensas
- **Penalidade por atraso**: perda de HP e possível perda de nível
- **Loja**: Poção de Café, Energy Drink, Escudo, Espada
- **Inventário**: consumíveis e equipamentos
- **Amigos**: pedidos por username e ranking por XP total
- **Admin Django**: visualizar usuários, stats (nível, XP, ouro), ativar/desativar acesso

## Estrutura do projeto

```
dungeons-deadlines/
├── core/
│   ├── models.py           # Usuario, Avatar, Task, Item, Inventory, Friendship, ActiveEffect
│   ├── views.py            # CBVs das páginas
│   ├── forms.py            # Formulários
│   ├── admin.py            # Admin estendido
│   ├── services/game.py    # Regras RPG (XP, ouro, atrasos, loja)
│   ├── static/css/game.css # Tema MMORPG
│   ├── templates/core/     # Templates da aplicação
│   └── tests/              # Testes unitários
├── templates/
│   ├── base.html
│   └── registration/login.html
└── dungeons_deadlines/
    ├── settings.py
    └── urls.py
```

## Modelos principais

### Usuario (AbstractUser)
- `email` (login), `username`, `full_name`, `birth_date`
- `is_active` — controla acesso à plataforma
- `is_staff` / `is_superuser` — acesso ao Django Admin

### Avatar
- `hp`, `max_hp`, `level`, `xp`, `total_xp`, `gold`

### Task
- `title`, `description`, `due_date`, `difficulty`, `is_completed`, `overdue_processed`

### Item / Inventory / ActiveEffect / Friendship

## Testes

```bash
python manage.py test core.tests
```

## Documentação completa

[Dungeons & Deadlines — Google Doc](https://docs.google.com/document/d/1EpjMv38__JNYI5DoP1IFRE8qk7r81He-Vx44eUlvbvE/edit?usp=sharing)
