from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils import timezone

from core.helpers import BeardOptions, ClothesOptions, ColorOptions, EyeOptions, GlassesOptions, HairOptions, HatOptions, MouthOptions
from core.models import Avatar, Friendship, Task, Usuario


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
            if not self.instance.can_edit:
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


class AvatarAppearanceForm(forms.Form):
    CLOTHES_CHOICES = [(choice.value, f"Roupa {index+1}") for index, choice in enumerate(ClothesOptions)]
    EYE_CHOICES = [(choice.value, f"Olho {index+1}") for index, choice in enumerate(EyeOptions)]
    HAIR_CHOICES = [(choice.value, f"Cabelo {index+1}") for index, choice in enumerate(HairOptions)]
    MOUTH_CHOICES = [(choice.value, f"Boca {index+1}") for index, choice in enumerate(MouthOptions)]
    GLASSES_CHOICES = [(None, "Sem Óculos")] + [
        (choice.value, f"Óculos {index+1}")  
        for index, choice in enumerate(GlassesOptions)
    ]
    HAT_CHOICES = [(None, "Sem Boné")] + [
        (choice.value, f"Boné {index+1}")
        for index, choice in enumerate(HatOptions)
    ]
    BEARD_CHOICES = [(None, "Sem Barba")] + [
        (choice.value, f"Barba {index+1}")
        for index, choice in enumerate(BeardOptions)
    ]

    COLOR_CHOICES = [
        (ColorOptions.YELLOW.value, "Amarelo Claro"),
        (ColorOptions.LIGHT_GRAY.value, "Cinza Claro"),
        (ColorOptions.GRAY.value, "Cinza Médio"),
        (ColorOptions.DARK_GRAY.value, "Cinza Escuro"),
        (ColorOptions.BLACK.value, "Preto"),
        (ColorOptions.OLIVE.value, "Cinza Oliva"),
        (ColorOptions.LIGHT_BLUE.value, "Azul Claro"),
        (ColorOptions.BLUE.value, "Azul"),
        (ColorOptions.DARK_BLUE.value, "Azul Escuro"),
        (ColorOptions.BLUE_GRAY.value, "Azul Acinzentado"),
        (ColorOptions.BLUE_GRAY_OPAQUE.value, "Azul Escuro Opaco"),
        (ColorOptions.TURQUOISE.value, "Azul Turquesa"),
        (ColorOptions.ROYAL_BLUE.value, "Azul Royal"),
        (ColorOptions.PETROLEUM_BLUE.value, "Azul Petróleo"),
        (ColorOptions.LIGHT_GREEN.value, "Verde Claro"),
        (ColorOptions.GREEN.value, "Verde"),
        (ColorOptions.DARK_GREEN.value, "Verde Escuro"),
        (ColorOptions.DARK_GREEN_BLUE.value, "Verde Azulado Escuro"),
        (ColorOptions.MUSHROOM_GREEN.value, "Verde Musgo"),
        (ColorOptions.LIME_GREEN.value, "Verde Lima"),
        (ColorOptions.GREEN_FLAG.value, "Verde Bandeira"),
        (ColorOptions.LIGHT_RED.value, "Vermelho Claro"),
        (ColorOptions.RED.value, "Vermelho"),
        (ColorOptions.DARK_RED.value, "Vermelho Escuro"),
        (ColorOptions.DARK_PINK.value, "Rosa Escuro"),
        (ColorOptions.VIVID_RED.value, "Vermelho Vivo"),
        (ColorOptions.PINK.value, "Rosa"),
        (ColorOptions.BRICK_RED.value, "Vermelho Tijolo"),
        (ColorOptions.LIGHT_PINK_OPAQUE.value, "Rosa Claro Opaco"),
        (ColorOptions.PINK_OPAQUE.value, "Rosa Opaco"),
        (ColorOptions.PINK_VIVID.value, "Rosa Vivo"),
        (ColorOptions.LIGHT_YELLOW.value, "Amarelo Creme"),
        (ColorOptions.YELLOW_DARK.value, "Amarelo"),
        (ColorOptions.BEIGE_DARK.value, "Bege Escuro"),
        (ColorOptions.LIGHT_BEIGE.value, "Bege Claro"),
        (ColorOptions.BROWN_GRAY.value, "Marrom Acinzentado"),
        (ColorOptions.BROWN_DARK.value, "Marrom Escuro"),
        (ColorOptions.BROWN.value, "Marrom"),
        (ColorOptions.BROWN_RED.value, "Marrom Avermelhado"),
        (ColorOptions.BROWN_DARK_BLACK.value, "Marrom Escuro Quase Preto"),
        (ColorOptions.BROWN_SEPIA.value, "Marrom Sépia"),
        (ColorOptions.BROWN_LIGHT.value, "Marrom Claro"),
        (ColorOptions.BROWN_GOLD.value, "Marrom Dourado"),
        (ColorOptions.BROWN_MEDIUM.value, "Marrom Médio"),
        (ColorOptions.BROWN_TERRACOTA.value, "Marrom Terracota"),
        (ColorOptions.PURPLE.value, "Roxo")
    ]

    eyesVariant = forms.ChoiceField(label="Olhos", choices=EYE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    hairVariant = forms.ChoiceField(label="Cabelo", choices=HAIR_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    mouthVariant = forms.ChoiceField(label="Boca", choices=MOUTH_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    
    hairColor = forms.ChoiceField(label="Cor do Cabelo", choices=COLOR_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    eyesColor = forms.ChoiceField(label="Cor dos Olhos", choices=COLOR_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    mouthColor = forms.ChoiceField(label="Cor da Boca", choices=COLOR_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    skinColor = forms.ChoiceField(label="Cor da Pele", choices=COLOR_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    
    glassesVariant = forms.ChoiceField(label="Óculos", choices=GLASSES_CHOICES, help_text="glasses", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    hatVariant = forms.ChoiceField(label="Chapéu", choices=HAT_CHOICES, help_text="hat", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    beardVariant = forms.ChoiceField(label="Barba", choices=BEARD_CHOICES, help_text="beard", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    clothesVariant = forms.ChoiceField(label="Roupa", choices=CLOTHES_CHOICES, help_text="shirt", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    
    clothesColor = forms.ChoiceField(label="Cor da Roupa", choices=COLOR_CHOICES, help_text="shirt", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    glassesColor = forms.ChoiceField(label="Cor dos Óculos", choices=COLOR_CHOICES, help_text="glasses", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    hatColor = forms.ChoiceField(label="Cor do Chapéu", choices=COLOR_CHOICES, help_text="hat", disabled=False, required=False, widget=forms.Select(attrs={'class': 'form-input'}))


    def __init__(self, *args, user=None, cosmetic_items=[], **kwargs):
        self.user = user
        self.cosmetic_items = cosmetic_items
        super().__init__(*args, **kwargs)

        if not len(cosmetic_items):
            form_fields_linked = [
                field 
                for _, field in self.fields.items() 
                if len(field.help_text)
            ]
            for field in form_fields_linked:
                field.disabled = True

        for cosmetic in cosmetic_items:
            if not cosmetic.is_equipped:
                form_fields_linked = [
                    field 
                    for _, field in self.fields.items() 
                    if field.help_text == cosmetic.item.slug
                ]
                for field in form_fields_linked:
                    field.disabled = True

    def save(self):
        if self.user is None:
            return None
        
        clothes_variant = self.cleaned_data.get("clothesVariant")
        clothesColor = self.cleaned_data.get("clothesColor")
        if not clothes_variant:
            clothes_variant = ClothesOptions.VARIANT01.value
            clothesColor = ColorOptions.BLUE.value

        print(clothes_variant, clothesColor)
        return {
            "clothesVariant": clothes_variant,
            "eyesVariant": self.cleaned_data.get("eyesVariant"),
            "glassesVariant": self.cleaned_data.get("glassesVariant"),
            "hairVariant": self.cleaned_data.get("hairVariant"),
            "hatVariant": self.cleaned_data.get("hatVariant"),
            "mouthVariant": self.cleaned_data.get("mouthVariant"),
            "beardVariant": self.cleaned_data.get("beardVariant"),
            "hairColor": self.cleaned_data.get("hairColor"),
            "clothesColor": clothesColor,
            "eyesColor": self.cleaned_data.get("eyesColor"),
            "glassesColor": self.cleaned_data.get("glassesColor"),
            "hatColor": self.cleaned_data.get("hatColor"),
            "mouthColor": self.cleaned_data.get("mouthColor"),
            "skinColor": self.cleaned_data.get("skinColor")
        }

    def clean(self):
        cleaned_data = super().clean()
        optional_fields = ["glassesVariant", "hatVariant", "beardVariant"]
        
        for field in optional_fields:
            value = cleaned_data.get(field)
            if value == "None" or value == "":
                cleaned_data[field] = None                

        return cleaned_data

    @property
    def paginated_fields(self):
        """
        Agrupa os campos (variantes+cores ou cores isoladas) e os divide
        em 'páginas/etapas' de no máximo 3 itens cada.
        """
        all_groups = []
        rendered_colors = set()

        for name, field in self.fields.items():
            if "Variant" in name:
                base_name = name.replace("Variant", "")
                color_name = f"{base_name}Color"
                
                group = {
                    "is_grouped": True,
                    "label": field.label,
                    "variant_field": self[name],
                    "color_field": self[color_name] if color_name in self.fields else None
                }
                if color_name in self.fields:
                    rendered_colors.add(color_name)
                all_groups.append(group)

        for name, field in self.fields.items():
            if "Color" in name and name not in rendered_colors:
                all_groups.append({
                    "is_grouped": False,
                    "label": field.label,
                    "color_field": self[name]
                })

        chunk_size = 3
        pages = [all_groups[i:i + chunk_size] for i in range(0, len(all_groups), chunk_size)]
        return pages
