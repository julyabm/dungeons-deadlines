# Dungeons & Deadlines

Um aplicativo web que combina **gamificação RPG** com **gerenciamento de tarefas**. Transforme seus afazeres em uma aventura épica!

## Tecnologias

- **Backend**: Django 6.0.5
- **Banco de Dados**: PostgreSQL
- **Python**: 3.13+

## Instalação

### 1. Pré-requisitos

- Python 3.13+
- PostgreSQL instalado e rodando

### 2. Ambiente virtual

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

### 3. Dependências

```bash
pip install -r requirements.txt
```

### 4. Banco de dados

Edite `dungeons_deadlines/settings.py` com suas credenciais PostgreSQL e crie o banco:

```sql
CREATE DATABASE dungeons_deadlines;
```

### 5. Migrations e dados iniciais

```bash
python manage.py migrate
python manage.py seed_items
python manage.py createsuperuser
```

### 6. Servidor

```bash
python manage.py runserver --insecure
```

Acesse: `http://127.0.0.1:8000/`

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
