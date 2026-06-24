from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

LAYERS_DIR = Path(settings.BASE_DIR) / 'core' / 'static' / 'avatar' / 'layers'
SIZE = (128, 128)
OUTLINE = (20, 20, 30)


class Command(BaseCommand):
    help = 'Gera arquivos PNG de camadas cosméticas para avatares'

    def handle(self, *args, **options):
        LAYERS_DIR.mkdir(parents=True, exist_ok=True)
        self._create_wizard_hat()
        self._create_knight_armor()
        self._create_crown()
        self.stdout.write(self.style.SUCCESS(f'Camadas geradas em {LAYERS_DIR}'))

    def _save(self, name, image):
        image.save(LAYERS_DIR / name)

    def _create_wizard_hat(self):
        image = Image.new('RGBA', SIZE, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.polygon([(64, 8), (96, 48), (32, 48)], fill=(80, 40, 160), outline=OUTLINE)
        draw.rectangle((28, 44, 100, 56), fill=(80, 40, 160), outline=OUTLINE)
        draw.ellipse((58, 4, 70, 16), fill=(220, 220, 80), outline=OUTLINE)
        self._save('wizard_hat.png', image)

    def _create_knight_armor(self):
        image = Image.new('RGBA', SIZE, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((38, 68, 90, 118), fill=(140, 145, 155), outline=OUTLINE)
        draw.rectangle((52, 78, 76, 96), fill=(180, 185, 195), outline=OUTLINE)
        draw.line((64, 78, 64, 96), fill=OUTLINE, width=2)
        draw.polygon([(64, 68), (74, 78), (54, 78)], fill=(140, 145, 155), outline=OUTLINE)
        self._save('knight_armor.png', image)

    def _create_crown(self):
        image = Image.new('RGBA', SIZE, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((36, 40, 92, 52), fill=(220, 180, 40), outline=OUTLINE)
        for x in (42, 64, 86):
            draw.polygon([(x, 40), (x - 6, 24), (x + 6, 24)], fill=(220, 180, 40), outline=OUTLINE)
            draw.ellipse((x - 3, 22, x + 3, 28), fill=(200, 40, 40), outline=OUTLINE)
        self._save('crown.png', image)
