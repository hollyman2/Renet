from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from Account.models import Follower

User = get_user_model()


@receiver(post_save, sender=Follower)
def increase_followers_count(sender, instance, created, **kwargs):
    if created:
        profile = User.objects.get(user=instance.user)
        profile.count_of_followers += 1
        profile.save()


@receiver(post_delete, sender=Follower)
def decrease_followers_count(sender, instance, **kwargs):
    profile = User.objects.get(user=instance.user)
    profile.count_of_followers -= 1
    profile.save()
