from django import template

register = template.Library()

@register.filter
def dict_get(d, k):
    """Return d[k] if possible, else ''."""
    if d is None:
        return ''
    return d.get(k, 0)
# core/templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Safely get a value from a dict."""
    if dictionary is None:
        return None
    return dictionary.get(key)
