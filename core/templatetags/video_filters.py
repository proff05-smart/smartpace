from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    """
    Extract YouTube video ID from a full URL.
    """
    if not url:
        return ""
    match = re.search(r'(?:v=|youtu\.be/)([^&?/]+)', url)
    return match.group(1) if match else url
