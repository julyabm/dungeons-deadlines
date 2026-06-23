from django import template

from core.services.game import DIFFICULTIES, monster_for, xp_to_next

register = template.Library()


@register.filter
def monster(difficulty):
    return DIFFICULTIES.get(difficulty, {})


@register.filter
def xp_next(level):
    return xp_to_next(level)
