from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    if isinstance(d, dict):
        return d.get(key, '0')
    return ''

# templatetags/dict_extras.py
from django import template
register = template.Library()

@register.filter
def get_item(d, key):
    return d.get(key)
from django import template

register = template.Library()

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    """Safely get a value from a dict in templates."""
    if dictionary is None:
        return None
    return dictionary.get(key)
