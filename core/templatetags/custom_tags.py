from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get a dictionary value by key in Django templates."""
    if dictionary and key in dictionary:
        return dictionary[key]
    return 0
