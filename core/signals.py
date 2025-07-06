from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now

from .models import Profile, Post, Comment, Notification  # add Like if you have that model

# Create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Update last login time on login
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    user.profile.last_login_time = now()
    user.profile.save()

# Notify on comment creation
@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        if post.author != instance.user:
            Notification.objects.create(
                user=post.author,
                sender=instance.user,
                verb="commented on your post",
                post=post
            )

# Notify on like (if you use ManyToManyField for likes on Post)
@receiver(m2m_changed, sender=Post.likes.through)
def notify_post_like(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            if instance.author.id != user_id:
                Notification.objects.create(
                    user=instance.author,
                    sender_id=user_id,
                    verb="liked your post",
                    post=instance
                )
