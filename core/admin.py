from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from core.forms import UsuarioChangeForm, UsuarioCreationForm
from core.models import ActiveEffect, Avatar, Friendship, Inventory, Item, Task, Usuario


class AvatarInline(admin.StackedInline):
    model = Avatar
    can_delete = False
    extra = 0
    readonly_fields = ('level', 'xp', 'total_xp', 'gold', 'hp', 'max_hp')


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    inlines = [AvatarInline]
    list_display = ('username', 'full_name', 'email', 'is_active', 'is_staff', 'avatar_level', 'avatar_xp', 'avatar_gold')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    actions = ['activate_users', 'deactivate_users']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informações pessoais', {'fields': ('full_name', 'birth_date', 'first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'birth_date', 'password1', 'password2'),
        }),
    )

    @admin.display(description='Nível')
    def avatar_level(self, obj):
        return obj.avatar.level if hasattr(obj, 'avatar') else '-'

    @admin.display(description='XP')
    def avatar_xp(self, obj):
        return obj.avatar.xp if hasattr(obj, 'avatar') else '-'

    @admin.display(description='Ouro')
    def avatar_gold(self, obj):
        return obj.avatar.gold if hasattr(obj, 'avatar') else '-'

    @admin.action(description='Ativar usuários selecionados')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuário(s) ativado(s).', messages.SUCCESS)

    @admin.action(description='Desativar usuários selecionados')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} usuário(s) desativado(s).', messages.WARNING)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'difficulty', 'due_date', 'is_completed', 'overdue_processed')
    list_filter = ('difficulty', 'is_completed', 'overdue_processed')
    search_fields = ('title', 'user__username')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'item_type', 'icon')
    search_fields = ('name', 'slug')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('avatar', 'item', 'quantity', 'is_equipped')
    list_filter = ('is_equipped', 'item__item_type')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'status')
    list_filter = ('status',)


@admin.register(ActiveEffect)
class ActiveEffectAdmin(admin.ModelAdmin):
    list_display = ('avatar', 'kind', 'expires_at')
    list_filter = ('kind',)
