from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Guarantees every User (including ones made via createsuperuser) has a
    Profile, so templates/views can always safely access `user.profile`.
    Registration views update this profile's role/details afterwards.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
