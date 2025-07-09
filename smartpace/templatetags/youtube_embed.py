from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(value):
    """
    Extracts YouTube video ID and formats it for embed.
    """
    regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})'
    match = re.search(regex, value)
    if match:
        return f"https://www.youtube.com/embed/{match.group(1)}"
    return ""

blog/templatetags/youtube_extras.py

