from django.contrib import admin
from .models import User,CustomerProfile, DriverProfile,Restaurant, MenuItem, Order, OrderItem ,Review
# Register your models here.
admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(DriverProfile)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)

