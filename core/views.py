from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.http.request import RAISE_ERROR, BadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
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
from core.models import Friendship, Inventory, Item, Task, Usuario
from core.services.avatar_renderer import render_avatar_png
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
        avatar = self.request.user.avatar
        items = context['inventory_items']
        context['appearance_form'] = AvatarAppearanceForm(instance=avatar)
        context['cosmetic_items'] = [row for row in items if row.item.item_type == 'Cosmético']
        context['game_items'] = [row for row in items if row.item.item_type != 'Cosmético']
        context['equipped_cosmetics'] = {
            row.item.cosmetic_slot: row
            for row in items
            if row.item.item_type == 'Cosmético' and row.is_equipped
        }
        return context


class AvatarAppearanceView(GameContextMixin, View):
    def post(self, request):
        avatar = request.user.avatar
        form = AvatarAppearanceForm(request.POST, instance=avatar)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'ok': True})
            messages.success(request, 'Aparência do avatar atualizada!')
            return redirect('profile')

        if is_ajax:
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

        for error in form.errors.values():
            messages.error(request, error.as_text())
        return redirect('profile')


class AvatarImageView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        target = get_object_or_404(Usuario, pk=user_id)
        if not hasattr(target, 'avatar'):
            raise Http404

        viewer = request.user
        if target != viewer and not _can_view_avatar(viewer, target):
            raise Http404

        png = render_avatar_png(target.avatar)
        return HttpResponse(png, content_type='image/png')


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
