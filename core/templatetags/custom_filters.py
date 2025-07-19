from django import template

register = template.Library()

@register.filter
def cap_score(value):
    try:
        return min(float(value), 10.0)
    except (ValueError, TypeError):
        return 0.0

@register.filter
def cap_score_js(value):
    try:
        return round(min(float(value), 10.0), 2)
    except (ValueError, TypeError):
        return 0.0

@register.filter
def my_filter(value):
    return value.upper()
