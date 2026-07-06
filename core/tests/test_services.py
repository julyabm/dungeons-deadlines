from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.models import Avatar, Inventory, Item, Task, Usuario
from core.services.game import (
    buy_item,
    complete_task,
    process_overdue,
    task_rewards,
    toggle_equip,
    use_item,
)


class GameServiceTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='player@test.com',
            username='player',
            full_name='Player One',
            password='pass1234',
        )
        self.avatar = self.user.avatar
        self.avatar.gold = 500
        self.avatar.save()

        self.coffee = Item.objects.create(
            slug='coffee',
            name='Poção de Café',
            price=30,
            item_type='Consumível',
            description='HP',
            icon='☕',
        )
        self.shield = Item.objects.create(
            slug='shield',
            name='Escudo',
            price=150,
            item_type='Equipamento',
            description='Shield',
            icon='🛡️',
        )

    def test_task_rewards(self):
        xp, gold = task_rewards('Fácil')
        self.assertEqual((xp, gold), (100, 5))

    def test_complete_task_awards_xp_and_gold(self):
        task = Task.objects.create(
            user=self.user,
            title='Slime',
            due_date=timezone.now() + timedelta(days=1),
            difficulty='Fácil',
        )
        complete_task(task)
        self.avatar.refresh_from_db()
        self.assertEqual(self.avatar.xp, 100)
        self.assertEqual(self.avatar.gold, 505)
        self.assertEqual(self.avatar.total_xp, 100)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)

    def test_process_overdue_applies_damage(self):
        task = Task.objects.create(
            user=self.user,
            title='Late task',
            due_date=timezone.now() - timedelta(hours=1),
            difficulty='Fácil',
        )
        results = process_overdue(self.avatar)
        self.avatar.refresh_from_db()
        task.refresh_from_db()
        self.assertEqual(self.avatar.hp, 50)
        self.assertTrue(task.overdue_processed)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['damage'], 50)

    def test_buy_item(self):
        buy_item(self.avatar, self.coffee)
        self.avatar.refresh_from_db()
        self.assertEqual(self.avatar.gold, 470)
        self.assertTrue(
            Inventory.objects.filter(avatar=self.avatar, item=self.coffee, quantity=1).exists()
        )

    def test_use_coffee(self):
        buy_item(self.avatar, self.coffee)
        row = Inventory.objects.get(avatar=self.avatar, item=self.coffee)
        self.avatar.hp = 50
        self.avatar.save()
        use_item(self.avatar, row)
        self.avatar.refresh_from_db()
        self.assertEqual(self.avatar.hp, 70)

    def test_toggle_equip(self):
        buy_item(self.avatar, self.shield)
        row = Inventory.objects.get(avatar=self.avatar, item=self.shield)
        toggle_equip(row)
        row.refresh_from_db()
        self.assertTrue(row.is_equipped)
