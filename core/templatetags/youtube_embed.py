# # your_app/templatetags/youtube_embed.py
# import re
# from django import template
# from django.utils.safestring import mark_safe

# register = template.Library()

# YOUTUBE_REGEX = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([^\s&]+))'

# @register.filter
# def embed_youtube_links(text):
#     def replacer(match):
#         url = match.group(1)
#         video_id = match.group(2)
#         embed_html = f'''
#         <div class="ratio ratio-16x9 my-3">
#             <iframe width="560" height="315" 
#                 src="https://www.youtube.com/embed/{video_id}" 
#                 title="YouTube video player" frameborder="0" 
#                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
#                 allowfullscreen></iframe>
#         </div>
#         '''
#         return embed_html

#     return mark_safe(re.sub(YOUTUBE_REGEX, replacer, text))
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

YOUTUBE_REGEX = r'(https?://(?:www\.)?youtube\.com/watch\?v=([-\w]+)|https?://youtu\.be/([-\w]+))'

@register.filter
def embed_youtube_links(value):
    def replacer(match):
        video_id = match.group(2) or match.group(3)
        embed_code = f'''
            <div class="ratio ratio-16x9 mb-3">
                <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>
            </div>
        '''
        return embed_code

    return mark_safe(re.sub(YOUTUBE_REGEX, replacer, value))
