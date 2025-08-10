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
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get value from dict by key in templates"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return 0
from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extracts the YouTube video ID from a full URL.
    Works with regular and shortened YouTube links.
    """
    if not url:
        return ""

    # Match common YouTube URL formats
    pattern = (
        r'(?:https?:\/\/)?'      # Optional scheme
        r'(?:www\.)?'            # Optional www
        r'(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)'  # Domain and path
        r'([a-zA-Z0-9_-]{11})'   # Video ID (11 chars)
    )
    match = re.search(pattern, url)
    return match.group(1) if match else url
