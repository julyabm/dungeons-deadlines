from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils import timezone

from core.models import Friendship, Task, Usuario


class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email', 'username', 'full_name', 'birth_date')


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = (
            'email', 'username', 'full_name', 'birth_date',
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
        )


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label='Nome completo',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Seu nome de herói'}),
    )
    birth_date = forms.DateField(
        label='Data de nascimento',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
    )
    username = forms.CharField(
        label='Nome de usuário',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'heroi123'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'heroi@email.com'}),
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = Usuario
        fields = ('full_name', 'birth_date', 'username', 'email', 'password1', 'password2')

    def clean_full_name(self):
        name = self.cleaned_data['full_name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Nome muito curto.')
        return name


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'due_date', 'difficulty')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Derrotar o monstro...'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'due_date': forms.DateTimeInput(
                attrs={'class': 'form-input', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'difficulty': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, user=None, is_edit=False, **kwargs):
        self.user = user
        self.is_edit = is_edit
        super().__init__(*args, **kwargs)
        self.fields['due_date'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        now = timezone.now()

        if not self.is_edit and due_date <= now:
            raise forms.ValidationError('A data de entrega deve ser no futuro.')

        if self.is_edit and self.instance.pk:
            if self.instance.due_date - now < timezone.timedelta(hours=24):
                raise forms.ValidationError('Não é possível editar tarefas a menos de 24h do prazo.')

        return due_date

    def save(self, commit=True):
        task = super().save(commit=False)
        if self.user:
            task.user = self.user
        if commit:
            task.save()
        return task


class FriendRequestForm(forms.Form):
    username = forms.CharField(
        label='Nome de usuário do amigo',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'username'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username:
            raise forms.ValidationError('Informe um nome de usuário.')

        if self.user and username == self.user.username:
            raise forms.ValidationError('Você não pode adicionar a si mesmo.')

        try:
            self.friend = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            raise forms.ValidationError('Usuário não encontrado.')

        if Friendship.objects.filter(
            user_from=self.user,
            user_to=self.friend,
        ).exists() or Friendship.objects.filter(
            user_from=self.friend,
            user_to=self.user,
        ).exists():
            raise forms.ValidationError('Amizade já existe ou está pendente.')

        return username

    def save(self):
        return Friendship.objects.create(
            user_from=self.user,
            user_to=self.friend,
            status='Pendente',
        )
