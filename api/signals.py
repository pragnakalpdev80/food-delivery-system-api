from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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

@receiver(post_save, sender=CustomerProfile)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(customer=instance)

@receiver(post_save, sender=Order)
def create_cart(sender, instance, created, **kwargs):
    if created:
        print("Hello")
        print(instance.restaurant.id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"restaurant_{instance.restaurant.id}",
            {
                "type": "new_order",
                "order_id": str(instance.order_number),
                "message": "New Order Recieved!"
            }
        )   