from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(value):
    """
    Extracts YouTube video ID and returns the embed URL.
    """
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})'
    match = re.search(pattern, value)
    if match:
        return f"https://www.youtube.com/embed/{match.group(1)}"
    return ""

@register.filter
def is_youtube_link(url):
    """
    Returns True if the URL is a YouTube video link.
    """
    if not url:
        return False
    return 'youtube.com' in url or 'youtu.be' in url
