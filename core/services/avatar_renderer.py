import io
from pathlib import Path

from django.conf import settings
from django.db.models import Case, IntegerField, Value, When
from PIL import Image, ImageDraw

from core.models import Inventory

AVATAR_SIZE = (192, 192)
LOGICAL_SIZE = (48, 48)
LAYERS_DIR = Path(settings.BASE_DIR) / 'core' / 'static' / 'avatar' / 'layers'

SKIN_COLORS = {
    'light': (245, 208, 169),
    'medium': (198, 134, 88),
    'dark': (120, 72, 48),
    'pale': (255, 224, 210),
    'tan': (210, 161, 100),
    'olive': (168, 130, 80),
    'deep': (75, 40, 20),
}

HAIR_COLORS = {
    'black': (30, 30, 30),
    'brown': (90, 55, 30),
    'blonde': (220, 180, 80),
    'red': (180, 60, 40),
    'white': (240, 240, 240),
    'gray': (160, 160, 160),
    'blue': (60, 100, 210),
    'green': (60, 160, 80),
    'purple': (130, 60, 180),
    'pink': (220, 100, 150),
}

OUTLINE = (20, 20, 30)
SHIRT_COLOR = (70, 100, 180)


def _new_canvas():
    image = Image.new('RGBA', LOGICAL_SIZE, (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def _draw_base_avatar(avatar):
    image, draw = _new_canvas()  # 48×48 RGBA canvas
    skin = SKIN_COLORS.get(avatar.skin_tone, SKIN_COLORS['medium'])
    hair = HAIR_COLORS.get(avatar.hair_color, HAIR_COLORS['brown'])

    # --- Body (shirt) ---
    draw.rectangle([16, 28, 31, 47], fill=SHIRT_COLOR, outline=OUTLINE)

    # --- Head (ellipse) ---
    draw.ellipse([13, 8, 34, 28], fill=skin, outline=OUTLINE)

    # --- Hair ---
    hair_style = avatar.hair_style
    if hair_style == 'bald':
        pass  # no hair
    elif hair_style == 'short':
        # Arc across crown + strip
        draw.arc([12, 4, 35, 22], start=200, end=340, fill=hair, width=3)
        draw.rectangle([13, 8, 34, 14], fill=hair, outline=OUTLINE)
    elif hair_style == 'long':
        # Arc + crown strip + side panels
        draw.arc([11, 3, 36, 23], start=180, end=360, fill=hair, width=3)
        draw.rectangle([13, 8, 34, 15], fill=hair, outline=OUTLINE)
        draw.rectangle([11, 14, 15, 35], fill=hair, outline=OUTLINE)
        draw.rectangle([32, 14, 36, 35], fill=hair, outline=OUTLINE)
    elif hair_style == 'spiky':
        for x in (14, 19, 24, 29):
            draw.polygon([(x, 14), (x + 2, 6), (x + 4, 14)], fill=hair, outline=OUTLINE)
    elif hair_style == 'curly':
        # Four small filled ellipses arranged in arc above head
        for cx, cy in [(16, 11), (20, 7), (25, 7), (30, 10)]:
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=hair, outline=OUTLINE)
    elif hair_style == 'ponytail':
        # Crown strip + tail
        draw.rectangle([13, 8, 34, 13], fill=hair, outline=OUTLINE)
        draw.rectangle([30, 13, 35, 28], fill=hair, outline=OUTLINE)
    elif hair_style == 'mohawk':
        # Narrow tall crest centered on crown (cols 22-25, rows 2-10)
        draw.rectangle([22, 2, 25, 10], fill=hair, outline=OUTLINE)
    else:
        # Fallback: short
        draw.arc([12, 4, 35, 22], start=200, end=340, fill=hair, width=3)
        draw.rectangle([13, 8, 34, 14], fill=hair, outline=OUTLINE)

    # --- Eyes ---
    draw.ellipse([17, 18, 21, 20], fill=OUTLINE)
    draw.ellipse([26, 18, 30, 20], fill=OUTLINE)

    # --- Mouth (smile arc) ---
    draw.arc([18, 22, 29, 25], start=10, end=170, fill=OUTLINE, width=1)

    # --- Upscale to 192×192 with pixel art (NEAREST) ---
    image = image.resize(AVATAR_SIZE, Image.Resampling.NEAREST)
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
        .annotate(
            slot_order=Case(
                When(item__cosmetic_slot='body', then=Value(0)),
                When(item__cosmetic_slot='face', then=Value(1)),
                When(item__cosmetic_slot='head', then=Value(2)),
                default=Value(9),
                output_field=IntegerField(),
            )
        )
        .order_by('slot_order')
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
