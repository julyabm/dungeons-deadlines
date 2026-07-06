from django import template

from core.services.game import DIFFICULTIES, monster_for, xp_to_next

register = template.Library()


@register.filter(name='replace_string')
def replace_string(value, args):
    search, replace = args.split(',')
    return value.replace(search, replace)

@register.filter(name='has_field')
def has_field(form, field_name):
    return field_name in form.fields

@register.filter
def monster(difficulty):
    return DIFFICULTIES.get(difficulty, {})

@register.filter
def xp_next(level):
    return xp_to_next(level)
