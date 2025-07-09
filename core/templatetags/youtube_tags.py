from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(value):
    """
    Extracts YouTube video ID and returns embed URL.
    """
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})'
    match = re.search(pattern, value)
    if match:
        return f"https://www.youtube.com/embed/{match.group(1)}"
    return ""
