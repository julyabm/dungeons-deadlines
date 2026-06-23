from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from core.models import Usuario


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            email='view@test.com',
            username='viewuser',
            full_name='View User',
            password='pass1234',
        )

    def test_landing_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_register_and_login(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'New Hero',
            'birth_date': '2000-01-01',
            'username': 'newhero',
            'email': 'new@test.com',
            'password1': 'Her0Secret!2024',
            'password2': 'Her0Secret!2024',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(email='new@test.com').exists())

        logged_in = self.client.login(username='new@test.com', password='Her0Secret!2024')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_inactive_user_redirected(self):
        self.user.is_active = False
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('account_disabled'))

    def test_create_task(self):
        self.client.login(username='view@test.com', password='pass1234')
        due = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(reverse('task_create'), {
            'title': 'Test Task',
            'description': 'Desc',
            'due_date': due,
            'difficulty': 'Fácil',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.tasks.count(), 1)
