from django.core.management.base import BaseCommand

from core.models import Item
from core.services.game import SHOP_ITEMS


class Command(BaseCommand):
    help = 'Popula a loja com os itens padrão do jogo'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item_data in SHOP_ITEMS:
            defaults = {
                'name': item_data['name'],
                'description': item_data['description'],
                'price': item_data['price'],
                'item_type': item_data['item_type'],
                'bonus_value': item_data['bonus_value'],
                'icon': item_data['icon']
            }
            _, created = Item.objects.update_or_create(
                slug=item_data['slug'],
                defaults=defaults,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Itens sincronizados: {created_count} criado(s), {updated_count} atualizado(s).'
            )
        )
