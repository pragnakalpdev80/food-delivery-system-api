from django.contrib import admin
from .models import (
    User, CustomerProfile, DriverProfile, 
    Restaurant, Address, MenuItem, Cart, 
    CartItem, Order, OrderItem, Review
)
# Register your models here.
admin.site.register(User)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CustomerProfile)
admin.site.register(DriverProfile)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)

