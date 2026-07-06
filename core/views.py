from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from core.forms import AvatarAppearanceForm, FriendRequestForm, RegisterForm, TaskForm
from core.mixins import GameContextMixin, SuccessMessageMixin
from core.models import Avatar, Friendship, Inventory, Item, Task, Usuario
from core.services.avatar_build import get_avatar_svg_url
from core.services.game import (
    DIFFICULTIES,
    buy_item,
    complete_task,
    toggle_equip,
    use_item,
)


class LandingView(TemplateView):
    template_name = 'core/landing.html'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Herói criado! Bem-vindo à aventura.')
        return response


class AccountDisabledView(TemplateView):
    template_name = 'core/account_disabled.html'


class DashboardView(GameContextMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_tasks'] = Task.objects.filter(
            user=self.request.user,
            is_completed=False,
        ).order_by('due_date')[:5]
        context['difficulties'] = DIFFICULTIES
        return context


class TaskListView(GameContextMixin, ListView):
    model = Task
    template_name = 'core/tasks/list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        tasks = context['tasks']
        context['pending_tasks'] = tasks.filter(is_completed=False, due_date__gte=now)
        context['overdue_tasks'] = tasks.filter(is_completed=False, due_date__lt=now)
        context['completed_tasks'] = tasks.filter(is_completed=True)
        return context


class TaskCreateView(GameContextMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/tasks/form.html'
    success_url = reverse_lazy('tasks')
    success_message = 'Tarefa criada com sucesso!'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova tarefa'
        return context


class TaskUpdateView(GameContextMixin, SuccessMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/tasks/form.html'
    success_url = reverse_lazy('tasks')
    success_message = 'Tarefa atualizada.'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, is_completed=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['is_edit'] = True
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar tarefa'
        return context


class TaskDeleteView(GameContextMixin, SuccessMessageMixin, DeleteView):
    model = Task
    template_name = 'core/tasks/confirm_delete.html'
    success_url = reverse_lazy('tasks')
    success_message = 'Tarefa removida.'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCompleteView(GameContextMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        try:
            complete_task(task)
            messages.success(request, f'Monstro derrotado! Recompensas coletadas.')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect(request.POST.get('next') or reverse('tasks'))


class DailyTasksView(GameContextMixin, ListView):
    model = Task
    template_name = 'core/daily.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        today = timezone.localdate()
        return Task.objects.filter(
            user=self.request.user,
            is_completed=False,
            due_date__date=today,
        ).order_by('due_date')


class ShopView(GameContextMixin, TemplateView):
    template_name = 'core/shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.all().order_by('price')
        context['consumable_items'] = items.filter(item_type='Consumível')
        context['equipment_items'] = items.filter(item_type='Equipamento')
        context['cosmetic_items'] = items.filter(item_type='Cosmético')
        owned = Inventory.objects.filter(
            avatar=self.request.user.avatar,
            quantity__gt=0,
        ).values_list('item_id', flat=True)
        context['owned_item_ids'] = set(owned)
        return context


class BuyItemView(GameContextMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        try:
            buy_item(request.user.avatar, item)
            messages.success(request, f'{item.name} comprado!')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('shop')


class ProfileView(GameContextMixin, ListView):
    model = Inventory
    template_name = 'core/profile.html'
    context_object_name = 'inventory_items'

    def get_queryset(self):
        return Inventory.objects.filter(
            avatar=self.request.user.avatar,
            quantity__gt=0,
        ).select_related('item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = context['inventory_items']
        avatar = self.request.user.avatar
        avatar_props = {
            "clothesVariant": avatar.clothesVariant,
            "eyesVariant": avatar.eyesVariant,
            "glassesVariant": avatar.glassesVariant,
            "hairVariant": avatar.hairVariant,
            "hatVariant": avatar.hatVariant,
            "mouthVariant": avatar.mouthVariant,
            "beardVariant": avatar.beardVariant,
            "hairColor": avatar.hairColor,
            "clothesColor": avatar.clothesColor,
            "eyesColor": avatar.eyesColor,
            "glassesColor": avatar.glassesColor,
            "hatColor": avatar.hatColor,
            "mouthColor": avatar.mouthColor,
            "skinColor": avatar.skinColor
        }
        context['avatar'] = avatar
        context['cosmetic_items'] = [row for row in items if row.item.item_type == 'Cosmético']
        context['appearance_form'] = AvatarAppearanceForm(
            user=self.request.user,
            cosmetic_items=context['cosmetic_items'],
            initial=avatar_props,
        )
        context['game_items'] = [row for row in items if row.item.item_type != 'Cosmético']
        return context


class AvatarAppearanceView(GameContextMixin, View):
    def post(self, request):
        try:
            cosmetic_items = Inventory.objects.filter(
                avatar=self.request.user.avatar,
                quantity__gt=0,
                item__item_type="Cosmético"
            ).select_related('item')
            
            form = AvatarAppearanceForm(request.POST, user=request.user, cosmetic_items=cosmetic_items)
            if form.is_valid():
                avatar_params = form.save()
                Avatar.objects.filter(user=request.user).update(**avatar_params)
                messages.success(request, 'Aparência do avatar atualizada!')
                return redirect("profile")

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as ex:
            print("AvatarAppearanceView post: " + str(ex))
            messages.error(request, f"Erro ao atualizar seu avatar. Tente novamente.")
        return redirect('profile')


class AvatarImageView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        target = get_object_or_404(Usuario, pk=user_id)
        if not hasattr(target, 'avatar'):
            raise Http404

        viewer = request.user
        if target != viewer and not _can_view_avatar(viewer, target):
            raise Http404

        return redirect(
            get_avatar_svg_url(
                self.request.user.id, 
                **{
                    "clothesVariant": target.avatar.clothesVariant,
                    "eyesVariant": target.avatar.eyesVariant,
                    "glassesVariant": target.avatar.glassesVariant,
                    "hairVariant": target.avatar.hairVariant,
                    "hatVariant": target.avatar.hatVariant,
                    "mouthVariant": target.avatar.mouthVariant,
                    "beardVariant": target.avatar.beardVariant,
                    "hairColor": target.avatar.hairColor,
                    "clothesColor": target.avatar.clothesColor,
                    "eyesColor": target.avatar.eyesColor,
                    "glassesColor": target.avatar.glassesColor,
                    "hatColor": target.avatar.hatColor,
                    "mouthColor": target.avatar.mouthColor,
                    "skinColor": target.avatar.skinColor
                }
            )
        )


def _can_view_avatar(viewer, target):
    if viewer == target:
        return True
    return Friendship.objects.filter(
        Q(user_from=viewer, user_to=target) | Q(user_from=target, user_to=viewer),
        status__in=['Aceito', 'Pendente'],
    ).exists()


class UseItemView(GameContextMixin, View):
    def post(self, request, pk):
        row = get_object_or_404(
            Inventory,
            pk=pk,
            avatar__user=request.user,
            quantity__gt=0,
        )
        try:
            use_item(request.user.avatar, row)
            messages.success(request, f'{row.item.name} utilizado!')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('profile')


class ToggleEquipView(GameContextMixin, View):
    def post(self, request, pk):
        row = get_object_or_404(
            Inventory,
            pk=pk,
            avatar__user=request.user,
            quantity__gt=0,
        )
        try:
            row = toggle_equip(row)
            state = 'equipado' if row.is_equipped else 'desequipado'
            messages.success(request, f'{row.item.name} {state}.')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('profile')


class InventoryView(ProfileView):
    def get(self, request, *args, **kwargs):
        return redirect('profile')


class FriendsView(GameContextMixin, FormView):
    template_name = 'core/friends.html'
    form_class = FriendRequestForm
    success_url = reverse_lazy('friends')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Pedido de amizade enviado!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['pending_received'] = Friendship.objects.filter(
            user_to=user,
            status='Pendente',
        ).select_related('user_from', 'user_from__avatar')
        context['pending_sent'] = Friendship.objects.filter(
            user_from=user,
            status='Pendente',
        ).select_related('user_to', 'user_to__avatar')
        accepted = Friendship.objects.filter(
            Q(user_from=user) | Q(user_to=user),
            status='Aceito',
        ).select_related('user_from__avatar', 'user_to__avatar')

        friends = []
        for friendship in accepted:
            friend = friendship.user_to if friendship.user_from == user else friendship.user_from
            friends.append(friend)

        ranking = sorted(
            [user] + friends,
            key=lambda u: u.avatar.total_xp if hasattr(u, 'avatar') else 0,
            reverse=True,
        )
        context['ranking'] = ranking
        return context


class FriendshipAcceptView(GameContextMixin, View):
    def post(self, request, pk):
        friendship = get_object_or_404(
            Friendship,
            pk=pk,
            user_to=request.user,
            status='Pendente',
        )
        friendship.status = 'Aceito'
        friendship.save(update_fields=['status'])
        messages.success(request, f'Amizade com {friendship.user_from.username} aceita!')
        return redirect('friends')


class FriendshipRejectView(GameContextMixin, View):
    def post(self, request, pk):
        friendship = get_object_or_404(
            Friendship,
            pk=pk,
            user_to=request.user,
            status='Pendente',
        )
        friendship.delete()
        messages.info(request, 'Pedido de amizade recusado.')
        return redirect('friends')


def bad_request(request, exception=None):
    return render(request, '400.html', status=400)


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)


def server_error(request):
    return render(request, '500.html', status=500)
