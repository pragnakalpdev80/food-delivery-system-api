from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "api"

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'drivers', views.DriverViewSet, basename='driver')
router.register(r'restaurants', views.RestaurantViewSet, basename='restaurant')
router.register(r'menu-items', views.MenuItemViewSet, basename='menu-item')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='orderitem')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', views.UserRegistrationView.as_view(), name='register'),
]