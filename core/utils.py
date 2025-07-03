# utils.py
from django.utils import timezone
from datetime import timedelta

def is_user_online(user):
    profile = getattr(user, 'userprofile', None)
    if profile:
        now = timezone.now()
        return now - profile.last_activity < timedelta(minutes=5)
    return False
