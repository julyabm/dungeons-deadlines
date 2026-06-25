from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    full_name = models.CharField(max_length=255, verbose_name='Nome Completo')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    objects = UsuarioManager()

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.username} ({self.full_name})'


class Avatar(models.Model):
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='avatar')
    hp = models.IntegerField(default=100, validators=[MinValueValidator(0)], verbose_name='Pontos de Vida')
    max_hp = models.IntegerField(default=100, validators=[MinValueValidator(1)], verbose_name='HP Máximo')
    level = models.IntegerField(default=1, verbose_name='Nível')
    xp = models.IntegerField(default=0, verbose_name='Experiência')
    total_xp = models.IntegerField(default=0, verbose_name='XP Total')
    gold = models.IntegerField(default=0, verbose_name='Ouro')

    clothesVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Roupa")
    eyesVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Olhos")
    glassesVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Óculos")
    hairVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Cabelo")
    hatVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Boné")
    mouthVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Boca")
    beardVariant = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de Barba")

    hairColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor de Cabelo")
    clothingColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor da Roupa")
    eyesColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor dos Olhos")
    glassesColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor dos Óculos")
    hatColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor do boné")
    mouthColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor da boca")
    skinColor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cor da pele")

    def __str__(self):
        return f'Avatar de {self.user.username} - Lvl {self.level}'

    @property
    def xp_to_next(self):
        return self.level * 1000


class Task(models.Model):
    DIFFICULTY_CHOICES = [
        ('Fácil', 'Fácil'),
        ('Médio', 'Médio'),
        ('Difícil', 'Difícil'),
    ]

    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=150, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    due_date = models.DateTimeField(verbose_name='Data de Entrega')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name='Dificuldade')
    is_completed = models.BooleanField(default=False, verbose_name='Concluída')
    overdue_processed = models.BooleanField(default=False, verbose_name='Atraso Processado')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Concluída em')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f'{self.title} ({self.user.username})'

    @property
    def is_overdue(self):
        from django.utils import timezone
        return not self.is_completed and self.due_date < timezone.now()

    @property
    def can_edit(self):
        from django.utils import timezone
        if self.is_completed:
            return False
        return self.due_date - timezone.now() > timezone.timedelta(hours=24)


class Item(models.Model):
    TYPE_CHOICES = [
        ('Consumível', 'Consumível'),
        ('Equipamento', 'Equipamento'),
        ('Cosmético', 'Cosmético'),
    ]

    slug = models.SlugField(max_length=50, unique=True, verbose_name='Identificador')
    name = models.CharField(max_length=100, verbose_name='Nome do Item')
    price = models.IntegerField(verbose_name='Preço (Ouro)')
    item_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Tipo')
    description = models.TextField(verbose_name='Descrição do Item')
    bonus_value = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Bônus')
    icon = models.CharField(max_length=10, default='📦', verbose_name='Ícone')

    def __str__(self):
        return self.name


class Inventory(models.Model):
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='inventory_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_equipped = models.BooleanField(default=False, verbose_name='Equipado')
    quantity = models.IntegerField(default=1, verbose_name='Quantidade')

    class Meta:
        verbose_name = 'Item no Inventário'
        verbose_name_plural = 'Itens no Inventário'
        unique_together = ('avatar', 'item')

    def __str__(self):
        return f'{self.item.name} x{self.quantity} ({self.avatar.user.username})'


class ActiveEffect(models.Model):
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='active_effects')
    kind = models.CharField(max_length=50, verbose_name='Tipo')
    expires_at = models.DateTimeField(verbose_name='Expira em')

    class Meta:
        unique_together = ('avatar', 'kind')

    def __str__(self):
        return f'{self.kind} ({self.avatar.user.username})'

    @property
    def is_active(self):
        from django.utils import timezone
        return self.expires_at > timezone.now()


class Friendship(models.Model):
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
        return f'{self.user_from.username} -> {self.user_to.username} ({self.status})'
