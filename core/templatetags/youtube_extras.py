import re
from django import template

register = template.Library()

@register.filter
def youtube_id(value):
    """
    Extract the YouTube video ID from a variety of formats.
    """
    regex = r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&?/]+)"
    match = re.search(regex, value)
    return match.group(1) if match else ""