import django_filters
from .models import Restaurant,MenuItem,Order, Review

class RestaurantFilter(django_filters.FilterSet):
    """ Restaurant filters """
    delivery_fee__lte = django_filters.NumberFilter(field_name='delivery_fee', lookup_expr='lte')
    minimum_order__lte = django_filters.NumberFilter(field_name='minimum_order', lookup_expr='lte')
    average_rating__gte = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')

    class Meta:
        model = Restaurant
        fields = ['cuisine_type', 'is_open', 'delivery_fee__lte', 'minimum_order__lte', 'average_rating__gte']

class MenuItemFilter(django_filters.FilterSet):
    """ Menu Items filters """
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = MenuItem
        fields = ['restaurant', 'category', 'dietary_info', 'is_available', 'price__lte']

class OrderFilter(django_filters.FilterSet):
    """ Order filters """
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Order
        fields = [ 'status', 'restaurant', 'created_at__gte']

class ReviewFilter(django_filters.FilterSet):
    """ Review filters """
    class Meta:
        model = Review
        fields = ['rating', 'restaurant','menu_item']