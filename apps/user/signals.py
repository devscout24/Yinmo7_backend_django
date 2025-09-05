from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import RepairShopProfile,CarOwnerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.type == 'repair_shop':
            RepairShopProfile.objects.create(user=instance)
        else:
            CarOwnerProfile.objects.create(user=instance)