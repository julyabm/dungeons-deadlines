from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.utils import timezone
from core.services.game import process_overdue
from core.services.avatar_build import get_avatar_svg_url

class ActiveUserMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_active:
            return redirect('account_disabled')
        return super().dispatch(request, *args, **kwargs)


class GameContextMixin(ActiveUserMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'avatar'):
            results = process_overdue(request.user.avatar)
            for result in results:
                task = result['task']
                damage = result['damage']
                messages.warning(
                    request,
                    f'A tarefa "{task.title}" venceu! Você perdeu {damage} HP.',
                )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and hasattr(self.request.user, 'avatar'):
            avatar = self.request.user.avatar
            avatar_url = get_avatar_svg_url(
                self.request.user.id, 
                **{
                    "clothesVariant": avatar.clothesVariant,
                    "eyesVariant": avatar.eyesVariant,
                    "glassesVariant": avatar.glassesVariant,
                    "hairVariant": avatar.hairVariant,
                    "hatVariant": avatar.hatVariant,
                    "mouthVariant": avatar.mouthVariant,
                    "beardVariant": avatar.beardVariant,
                    "hairColor": avatar.hairColor,
                    "clothingColor": avatar.clothingColor,
                    "eyesColor": avatar.eyesColor,
                    "glassesColor": avatar.glassesColor,
                    "hatColor": avatar.hatColor,
                    "mouthColor": avatar.mouthColor,
                    "skinColor": avatar.skinColor
                }
            )

            context['avatar'] = avatar
            context['avatar_url'] = avatar_url
            context['xp_to_next'] = avatar.xp_to_next
            context['active_xp_boost'] = avatar.active_effects.filter(
                kind='xp_boost',
                expires_at__gt=timezone.now(),
            ).first()
        return context


class SuccessMessageMixin:
    success_message = ''

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response
