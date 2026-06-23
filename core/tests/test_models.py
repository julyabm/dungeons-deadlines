from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.models import Avatar, Usuario


class AvatarSignalTests(TestCase):
    def test_avatar_created_on_user_registration(self):
        user = Usuario.objects.create_user(
            email='hero@test.com',
            username='hero',
            full_name='Hero Test',
            password='pass1234',
        )
        self.assertTrue(Avatar.objects.filter(user=user).exists())
        avatar = user.avatar
        self.assertEqual(avatar.level, 1)
        self.assertEqual(avatar.hp, 100)
        self.assertEqual(avatar.max_hp, 100)


class AvatarPropertyTests(TestCase):
    def test_xp_to_next(self):
        user = Usuario.objects.create_user(
            email='hero2@test.com',
            username='hero2',
            full_name='Hero Two',
            password='pass1234',
        )
        self.assertEqual(user.avatar.xp_to_next, 1000)
