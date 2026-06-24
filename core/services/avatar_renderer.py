import io
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw

from core.models import Inventory

AVATAR_SIZE = (128, 128)
LAYERS_DIR = Path(settings.BASE_DIR) / 'core' / 'static' / 'avatar' / 'layers'

SKIN_COLORS = {
    'light': (245, 208, 169),
    'medium': (198, 134, 88),
    'dark': (120, 72, 48),
}

HAIR_COLORS = {
    'black': (30, 30, 30),
    'brown': (90, 55, 30),
    'blonde': (220, 180, 80),
    'red': (180, 60, 40),
}

OUTLINE = (20, 20, 30)
SHIRT_COLOR = (70, 100, 180)


def _new_canvas():
    image = Image.new('RGBA', AVATAR_SIZE, (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def _draw_base_avatar(avatar):
    image, draw = _new_canvas()
    skin = SKIN_COLORS.get(avatar.skin_tone, SKIN_COLORS['medium'])
    hair = HAIR_COLORS.get(avatar.hair_color, HAIR_COLORS['brown'])

    draw.rectangle((44, 72, 84, 118), fill=SHIRT_COLOR, outline=OUTLINE)
    draw.ellipse((40, 34, 88, 82), fill=skin, outline=OUTLINE)

    if avatar.hair_style == 'short':
        draw.arc((36, 18, 92, 70), start=200, end=340, fill=hair, width=10)
        draw.rectangle((38, 28, 90, 44), fill=hair)
    elif avatar.hair_style == 'long':
        draw.arc((34, 14, 94, 74), start=180, end=360, fill=hair, width=12)
        draw.rectangle((36, 30, 92, 52), fill=hair)
        draw.rectangle((34, 44, 44, 96), fill=hair, outline=OUTLINE)
        draw.rectangle((84, 44, 94, 96), fill=hair, outline=OUTLINE)
    else:
        for x in range(42, 87, 8):
            draw.polygon([(x, 24), (x + 4, 12), (x + 8, 24)], fill=hair, outline=OUTLINE)

    draw.ellipse((52, 52, 60, 60), fill=(255, 255, 255, 255))
    draw.ellipse((68, 52, 76, 60), fill=(255, 255, 255, 255))
    draw.ellipse((54, 54, 58, 58), fill=OUTLINE)
    draw.ellipse((70, 54, 74, 58), fill=OUTLINE)
    draw.arc((54, 62, 74, 74), start=10, end=170, fill=OUTLINE, width=2)

    return image


def _load_layer(layer_file):
    path = LAYERS_DIR / layer_file
    if not path.exists():
        return None
    layer = Image.open(path).convert('RGBA')
    return layer.resize(AVATAR_SIZE, Image.Resampling.NEAREST)


def _equipped_cosmetics(avatar):
    return (
        Inventory.objects.filter(
            avatar=avatar,
            item__item_type='Cosmético',
            is_equipped=True,
            quantity__gt=0,
        )
        .select_related('item')
        .order_by('item__cosmetic_slot')
    )


def render_avatar_png(avatar):
    base = _draw_base_avatar(avatar)

    for row in _equipped_cosmetics(avatar):
        layer_file = row.item.layer_file
        if not layer_file:
            continue
        layer = _load_layer(layer_file)
        if layer:
            base = Image.alpha_composite(base, layer)

    buffer = io.BytesIO()
    base.save(buffer, format='PNG')
    return buffer.getvalue()
