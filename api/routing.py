from django.urls import re_path
from .consumers import (
    RestaurantDashboardConsumer,
    OrderConsumer,
    CustomerDashboardConsumer,
    DriverDashboardConsumer
)
"""
Websocket URL routes to connect with the websocket for communication.
"""
websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_number>[A-Za-z0-9_-]+)/$',OrderConsumer.as_asgi()),
    re_path(r'ws/restaurants/(?P<restaurant_id>\d+)/$',RestaurantDashboardConsumer.as_asgi()),
    re_path(r'ws/drivers/(?P<driver_id>\d+)/$',DriverDashboardConsumer.as_asgi()),
    re_path(r'ws/customers/(?P<customer_id>\d+)/$',CustomerDashboardConsumer.as_asgi()),
]   