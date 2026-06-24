from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.models import ActiveEffect, Avatar, Inventory, Item, Task

DIFFICULTIES = {
    'Fácil': {'monster': 'Slime', 'xp': 100, 'gold': 5, 'css_class': 'text-easy'},
    'Médio': {'monster': 'Ogro', 'xp': 200, 'gold': 15, 'css_class': 'text-medium'},
    'Difícil': {'monster': 'Dragão', 'xp': 500, 'gold': 50, 'css_class': 'text-hard'},
}

SHOP_ITEMS = [
    {
        'slug': 'coffee',
        'name': 'Poção de Café',
        'description': 'Recupera +20 HP instantaneamente.',
        'price': 30,
        'item_type': 'Consumível',
        'bonus_value': Decimal('20.00'),
        'icon': '☕',
    },
    {
        'slug': 'energy_drink',
        'name': 'Energy Drink',
        'description': '+25% XP em todas as tarefas por 2 horas.',
        'price': 60,
        'item_type': 'Consumível',
        'bonus_value': Decimal('25.00'),
        'icon': '⚡',
    },
    {
        'slug': 'shield',
        'name': 'Escudo',
        'description': 'Reduz em 50% o dano de tarefas atrasadas.',
        'price': 150,
        'item_type': 'Equipamento',
        'bonus_value': Decimal('50.00'),
        'icon': '🛡️',
    },
    {
        'slug': 'sword',
        'name': 'Espada',
        'description': '+10% de ouro por tarefa concluída.',
        'price': 200,
        'item_type': 'Equipamento',
        'bonus_value': Decimal('10.00'),
        'icon': '⚔️',
    },
    {
        'slug': 'wizard_hat',
        'name': 'Chapéu de Mago',
        'description': 'Cosmético para a cabeça do seu avatar.',
        'price': 80,
        'item_type': 'Cosmético',
        'bonus_value': Decimal('0.00'),
        'icon': '🎩',
        'cosmetic_slot': 'head',
        'layer_file': 'wizard_hat.png',
    },
    {
        'slug': 'knight_armor',
        'name': 'Armadura de Cavaleiro',
        'description': 'Cosmético para o corpo do seu avatar.',
        'price': 120,
        'item_type': 'Cosmético',
        'bonus_value': Decimal('0.00'),
        'icon': '🛡️',
        'cosmetic_slot': 'body',
        'layer_file': 'knight_armor.png',
    },
    {
        'slug': 'crown',
        'name': 'Coroa Real',
        'description': 'Cosmético exclusivo para a cabeça do avatar.',
        'price': 200,
        'item_type': 'Cosmético',
        'bonus_value': Decimal('0.00'),
        'icon': '👑',
        'cosmetic_slot': 'head',
        'layer_file': 'crown.png',
    },
]


def xp_to_next(level):
    return level * 1000


def task_rewards(difficulty):
    data = DIFFICULTIES[difficulty]
    return data['xp'], data['gold']


def monster_for(difficulty):
    return DIFFICULTIES[difficulty]


def _has_xp_boost(avatar):
    return ActiveEffect.objects.filter(
        avatar=avatar,
        kind='xp_boost',
        expires_at__gt=timezone.now(),
    ).exists()


def _has_equipped(avatar, slug):
    return Inventory.objects.filter(
        avatar=avatar,
        item__slug=slug,
        is_equipped=True,
        quantity__gt=0,
    ).exists()


def _apply_level_ups(avatar):
    while avatar.xp >= xp_to_next(avatar.level):
        avatar.xp -= xp_to_next(avatar.level)
        avatar.level += 1
        avatar.max_hp = 100 + (avatar.level - 1) * 20
        avatar.hp = avatar.max_hp


@transaction.atomic
def complete_task(task):
    if task.is_completed:
        raise ValueError('Tarefa já concluída')

    avatar = Avatar.objects.select_for_update().get(user=task.user)
    base_xp, base_gold = task_rewards(task.difficulty)

    gain_xp = int(base_xp * 1.25) if _has_xp_boost(avatar) else base_xp
    gain_gold = int(base_gold * 1.10) if _has_equipped(avatar, 'sword') else base_gold

    task.is_completed = True
    task.completed_at = timezone.now()
    task.save(update_fields=['is_completed', 'completed_at'])

    avatar.xp += gain_xp
    avatar.total_xp += gain_xp
    avatar.gold += gain_gold
    _apply_level_ups(avatar)
    avatar.save()
    return avatar


@transaction.atomic
def process_overdue(avatar):
    avatar = Avatar.objects.select_for_update().get(pk=avatar.pk)
    shield_equipped = _has_equipped(avatar, 'shield')

    overdue_tasks = Task.objects.select_for_update().filter(
        user=avatar.user,
        is_completed=False,
        due_date__lt=timezone.now(),
        overdue_processed=False,
    )

    results = []
    for task in overdue_tasks:
        base_xp, _ = task_rewards(task.difficulty)
        damage = base_xp // 2
        if shield_equipped:
            damage //= 2

        avatar.hp -= damage

        if avatar.hp <= 0:
            if avatar.hp < 0 and avatar.level > 1:
                avatar.level -= 1
                avatar.xp = 0
                avatar.max_hp = 100 + (avatar.level - 1) * 20
            avatar.hp = avatar.max_hp // 2

        task.overdue_processed = True
        task.save(update_fields=['overdue_processed'])
        results.append({'task': task, 'damage': damage})

    avatar.save()
    return results


@transaction.atomic
def buy_item(avatar, item):
    avatar = Avatar.objects.select_for_update().get(pk=avatar.pk)

    if avatar.gold < item.price:
        raise ValueError('Ouro insuficiente')

    inventory, created = Inventory.objects.get_or_create(
        avatar=avatar,
        item=item,
        defaults={'quantity': 0},
    )

    if item.item_type == 'Equipamento' and inventory.quantity > 0:
        raise ValueError('Item já possuído')

    if item.item_type == 'Cosmético' and inventory.quantity > 0:
        raise ValueError('Item já possuído')

    avatar.gold -= item.price
    avatar.save(update_fields=['gold'])

    inventory.quantity += 1
    inventory.save(update_fields=['quantity'])
    return avatar


@transaction.atomic
def use_item(avatar, inventory_row):
    avatar = Avatar.objects.select_for_update().get(pk=avatar.pk)

    if inventory_row.quantity <= 0:
        raise ValueError('Item não disponível no inventário')

    slug = inventory_row.item.slug

    if slug == 'coffee':
        avatar.hp = min(avatar.hp + 20, avatar.max_hp)
        avatar.save(update_fields=['hp'])
    elif slug == 'energy_drink':
        expires = timezone.now() + timedelta(hours=2)
        effect, _ = ActiveEffect.objects.get_or_create(
            avatar=avatar,
            kind='xp_boost',
            defaults={'expires_at': expires},
        )
        if effect.expires_at < expires:
            effect.expires_at = expires
            effect.save(update_fields=['expires_at'])
    else:
        raise ValueError('Item não consumível')

    inventory_row.quantity -= 1
    inventory_row.save(update_fields=['quantity'])
    return avatar


@transaction.atomic
def toggle_equip(inventory_row):
    if inventory_row.quantity <= 0:
        raise ValueError('Item não disponível no inventário')

    item = inventory_row.item
    if item.item_type not in ('Equipamento', 'Cosmético'):
        raise ValueError('Item não equipável')

    if item.item_type == 'Cosmético' and not inventory_row.is_equipped:
        Inventory.objects.filter(
            avatar=inventory_row.avatar,
            item__item_type='Cosmético',
            item__cosmetic_slot=item.cosmetic_slot,
            is_equipped=True,
        ).exclude(pk=inventory_row.pk).update(is_equipped=False)

    inventory_row.is_equipped = not inventory_row.is_equipped
    inventory_row.save(update_fields=['is_equipped'])
    return inventory_row
