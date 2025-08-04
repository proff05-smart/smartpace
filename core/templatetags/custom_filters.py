from django import template
import re

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

@register.filter
def youtube_id(value):
    """
    Extract the YouTube video ID from various YouTube URL formats.
    """
    regex = r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&?/]+)"
    match = re.search(regex, value)
    return match.group(1) if match else ""
