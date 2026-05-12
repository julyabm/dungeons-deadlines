from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# --- USER MANAGER ---
class UsuarioManager(BaseUserManager):
    def create_user(self, username, full_name, password=None):
        if not username:
            raise ValueError('O username é obrigatório')
        usuario = self.model(username=username, full_name=full_name)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, username, full_name, password):
        usuario = self.create_user(username, full_name, password)
        usuario.is_admin = True
        usuario.save(using=self._db)
        return usuario

# --- 1. USUÁRIO CUSTOMIZADO (RF02) ---
class Usuario(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True, verbose_name="Nome de Usuário")
    full_name = models.CharField(max_length=255, verbose_name="Nome Completo")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} ({self.full_name})"


# --- 2. AVATAR / PROGRESSO (RF04, RN03, RN04) ---
class Avatar(models.Model):
    """
    Armazena o progresso do RPG vinculado ao usuário.
    Requisito: RF04 e Regras de Negócio de XP/Nível.
    """
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='avatar')
    hp = models.IntegerField(default=100, validators=[MinValueValidator(0)], verbose_name="Pontos de Vida")
    level = models.IntegerField(default=1, verbose_name="Nível")
    xp = models.IntegerField(default=0, verbose_name="Experiência")
    gold = models.IntegerField(default=0, verbose_name="Ouro")

    def __str__(self):
        return f"Avatar de {self.user.username} - Lvl {self.level}"


# --- 3. TAREFAS (RF01, RF03, RF05, RF09, RN01, RN02, RN05, RN06) ---
class Task(models.Model):
    """
    Representa as tarefas a serem cumpridas.
    Requisito: RF01 e Regras de Negócio de Punição/Recompensa.
    """
    DIFFICULTY_CHOICES = [
        ('Fácil', 'Fácil'),
        ('Médio', 'Médio'),
        ('Difícil', 'Difícil'),
    ]

    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=150, verbose_name="Título")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    due_date = models.DateTimeField(verbose_name="Data de Entrega")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name="Dificuldade")
    is_completed = models.BooleanField(default=False, verbose_name="Concluída")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


# --- 4. ITENS DA LOJA (RF07, RN08) ---
class Item(models.Model):
    """
    Itens disponíveis para compra na loja do jogo.
    Requisito: RF07.
    """
    TYPE_CHOICES = [
        ('Consumível', 'Consumível'),
        ('Equipamento', 'Equipamento'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nome do Item")
    price = models.IntegerField(verbose_name="Preço (Ouro)")
    item_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Tipo")
    description = models.TextField(verbose_name="Descrição do Item")
    bonus_value = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Bônus")

    def __str__(self):
        return self.name


# --- 5. INVENTÁRIO (RF06, RN07, RN08) ---
class Inventory(models.Model):
    """
    Relaciona os itens comprados aos avatares dos usuários.
    Requisito: RF06.
    """
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='inventory_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_equipped = models.BooleanField(default=False, verbose_name="Equipado")
    quantity = models.IntegerField(default=1, verbose_name="Quantidade")

    class Meta:
        verbose_name = "Item no Inventário"
        verbose_name_plural = "Itens no Inventário"


# --- 6. AMIZADES (RF10) ---
class Friendship(models.Model):
    """
    Gerencia as conexões entre usuários.
    Requisito: RF10.
    """
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Aceito', 'Aceito'),
        ('Bloqueado', 'Bloqueado'),
    ]

    user_from = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='friendships_sent')
    user_to = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='friendships_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')

    class Meta:
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return f"{self.user_from.username} -> {self.user_to.username} ({self.status})"