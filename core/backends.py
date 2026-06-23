from django.contrib.auth.backends import ModelBackend


class GameAuthBackend(ModelBackend):
    """Permite sessão de usuários desativados (redirect), mas bloqueia login."""

    def user_can_authenticate(self, user):
        return True

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is not None and not user.is_active:
            return None
        return user
