from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "expense"

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'drivers', views.DriverViewSet, basename='driver')
router.register(r'restuarants', views.RestaurantViewSet, basename='restatirant')
router.register(r'menuitems', views.MenuItemViewSet, basename='menu-item')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'orderitems', views.OrderItemViewSet, basename='orderitem')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
]