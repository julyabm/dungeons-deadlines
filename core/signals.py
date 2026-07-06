from django.db.models.signals import post_save
from django.dispatch import receiver

from core.helpers import AvatarBuildOptions

from .models import Avatar, Usuario


@receiver(post_save, sender=Usuario)
def create_avatar_for_user(sender, instance, created, **kwargs):
    if created:
        avatar_options = AvatarBuildOptions()
        valid_fields = {f.name for f in Avatar._meta.fields}
        filtered_options = {
            k: v for k, v in avatar_options.__dict__.items() 
            if k in valid_fields
        }
        Avatar.objects.create(user=instance, **filtered_options)
