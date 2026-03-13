from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, CustomerProfile, DriverProfile, Restaurant

@receiver(post_save, sender=User)
def create_userprofile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'customer':
            CustomerProfile.objects.create(user=instance)
        elif instance.user_type == 'delivery_driver':
            DriverProfile.objects.create(user=instance) 
        elif instance.user_type == 'restaurant_owner':
            Restaurant.objects.create(owner=instance) 
