from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()  
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)  

@receiver(post_delete, sender=User)
def delete_profile(sender, instance, **kwargs):
    try:
        if instance.profile.profile_picture:
            instance.profile.profile_picture.delete(save=False)  
    except Profile.DoesNotExist:
        pass  