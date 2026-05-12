# 🐉 Dungeons & Deadlines

Um aplicativo web inovador que combina **gamificação RPG** com **gerenciamento de tarefas**. Transforme seus afazeres em uma aventura épica!

## 📋 Sobre o Projeto

Dungeons & Deadlines é uma plataforma que incentiva a produtividade através da mecânica de um jogo de RPG. Complete tarefas para ganhar experiência, subir de nível, acumular ouro e comprar itens na loja do jogo.

### Veja mais sobre o projeto em:

[Dungeons & Deadlines](https://docs.google.com/document/d/1EpjMv38__JNYI5DoP1IFRE8qk7r81He-Vx44eUlvbvE/edit?usp=sharing)


## 🛠️ Tecnologias

- **Backend**: Django 6.0.5
- **Banco de Dados**: PostgreSQL
- **Python**: 3.13+

---

## 📦 Instalação e Setup

### 1. Pré-requisitos
- Python 3.13 ou superior
- PostgreSQL instalado e rodando
- pip para gerenciamento de pacotes

### 2. Clonar o repositório
```bash
git clone https://github.com/julyabm/dungeons-deadlines.git
cd Dungeons_Deadlines
```

### 3. Criar e ativar o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar o banco de dados

Edite `dungeons_deadlines/settings.py` e verifique as credenciais do PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dungeons_deadlines',
        'USER': 'postgres',
        'PASSWORD': 'postgres',  # Altere conforme sua configuração
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Crie o banco de dados no PostgreSQL:
```sql
CREATE DATABASE dungeons_deadlines;
```

### 6. Executar migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Criar superusuário (admin)
```bash
python manage.py createsuperuser
```

### 8. Rodar o servidor
```bash
python manage.py runserver
```

O servidor estará disponível em: `http://127.0.0.1:8000/`

---

## 📁 Estrutura do Projeto

```
Dungeons_Deadlines/
├── manage.py                    # Gerenciador de comandos Django
├── db.sqlite3                   # Banco de dados (se usar SQLite)
├── requirements.txt             # Dependências do projeto
├── .gitignore                   # Arquivos ignorados pelo Git
├── .venv/                       # Ambiente virtual
├── core/                        # App principal
│   ├── migrations/              # Migrations do banco de dados
│   ├── models.py                # Modelos: Usuario, Avatar, Task, Item, etc.
│   ├── admin.py                 # Configuração do painel admin
│   ├── views.py                 # Lógica de views
│   ├── apps.py                  # Configuração da app
│   └── tests.py                 # Testes unitários
└── dungeons_deadlines/          # Configuração do projeto
    ├── settings.py              # Configurações do Django
    ├── urls.py                  # URLs principais
    ├── asgi.py                  # Configuração ASGI
    └── wsgi.py                  # Configuração WSGI
```

---

## 📊 Modelos do Banco de Dados

### Usuario
```python
- username (CharField, único)
- full_name (CharField)
- birth_date (DateField, opcional)
- is_active (BooleanField)
- is_admin (BooleanField)
```

### Avatar
```python
- user (OneToOneField -> Usuario)
- hp (IntegerField, default: 100)
- level (IntegerField, default: 1)
- xp (IntegerField, default: 0)
- gold (IntegerField, default: 0)
```

### Task
```python
- user (ForeignKey -> Usuario)
- title (CharField)
- description (TextField, opcional)
- due_date (DateTimeField)
- difficulty (CharField: Fácil, Médio, Difícil)
- is_completed (BooleanField, default: False)
- created_at (DateTimeField)
```

### Item
```python
- name (CharField)
- price (IntegerField)
- item_type (CharField: Consumível, Equipamento)
- description (TextField)
- bonus_value (DecimalField)
```

### Inventory
```python
- avatar (ForeignKey -> Avatar)
- item (ForeignKey -> Item)
- is_equipped (BooleanField)
- quantity (IntegerField, default: 1)
```

### Friendship
```python
- user_from (ForeignKey -> Usuario)
- user_to (ForeignKey -> Usuario)
- status (CharField: Pendente, Aceito, Bloqueado)
```

---