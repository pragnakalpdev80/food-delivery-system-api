from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def create_userprofile(sender, instance, created, **kwargs):
    """
    To Create Customer and Driver Profiles
    """
    if created:
        if instance.user_type == 'customer':
            CustomerProfile.objects.create(user=instance)
        elif instance.user_type == 'delivery_driver':
            DriverProfile.objects.create(user=instance) 

@receiver(post_save, sender=Review)
def update_rating_on_review_save(sender, instance, created, **kwargs):
    """
    To Update Average Rating
    """
    if created:
        if instance.restaurant:
            instance.restaurant.update_average_rating()
