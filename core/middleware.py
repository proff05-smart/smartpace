# middleware.py
import datetime
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class UpdateLastActivityMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None)
            if profile:
                profile.last_activity = timezone.now()
                profile.save()
