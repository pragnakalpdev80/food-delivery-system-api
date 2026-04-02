import logging
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from api.models import User
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import *
from api.pagination import *
from api.filters import *
from api.models import *
from api.permissions import *
from api.throttles import *

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []
 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)   
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,  
            'refresh': str(refresh),  
            'access': str(refresh.access_token),  
        }, status=status.HTTP_201_CREATED)  


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsCustomer]
    serializer_class = CustomerProfileSerializer
    queryset = CustomerProfile.objects.none()

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = AddressSerializer
    queryset = Address.objects.none()

    def get_queryset(self):
        return Address.objects.filter(user = self.request.user)
        

class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDriver]
    serializer_class = DriverProfileSerializer
    queryset = DriverProfile.objects.none()

    def get_queryset(self):
        return DriverProfile.objects.filter(user=self.request.user)


class RestaurantViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsRestaurantOwner, IsOwnerOrReadOnly]
    # permission_classes = []
    pagination_class = RestaurantPageNumberPagination
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    filterset_class = RestaurantFilter
    # filter_backends = [DjangoFilterBackend,]
    search_fields = ['name', 'cuisine_type', 'description']
    ordering_fields = ['-average_rating', 'delivery_fee', 'created_at',]
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'menu', 'popular']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsRestaurantOwner(), IsOwnerOrReadOnly()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantSerializer

    @method_decorator(cache_page(60 * 5), name='dispatch')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 10), name='dispatch')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15), name='dispatch')
    @action(detail=True, methods=['get'], url_path='menu')
    def menu(self, request,  *args, **kwargs):
        restaurant = self.get_object()
        items = MenuItem.objects.filter(restaurant_id=restaurant.id, is_available=True)
        print(items)
        serializer = MenuItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 30), name='dispatch')
    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request,  *args, **kwargs):
        popular = Restaurant.objects.filter(is_open=True).order_by('-average_rating')
        serializer = RestaurantSerializer(popular, many=True, context={'request': request})
        return Response(serializer.data)
    

class MenuItemViewSet(viewsets.ModelViewSet):
    pagination_class =MenuItemPageNumberPagination
    # queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at',]
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsRestaurantOwner(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'restaurant_owner':
            return MenuItem.objects.filter(restaurant__owner=user).select_related('restaurant')
        return MenuItem.objects.filter(is_available=True).select_related('restaurant')


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.prefetch_related('cart_items', 'cart_items__menu_item').filter(customer=self.request.user.customer_profile)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        try:
            cart = request.user.customer_profile.cart
            cart.cart_items.all().delete()
            cart.restaurant = None
            cart.save(update_fields=['restaurant', 'updated_at'])
        except Cart.DoesNotExist:
            pass
        return Response({'success': 'Cart cleared.'})


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user.customer_profile).select_related('menu_item')

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class =OrderCursorPagination
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['total_amount',]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return OrderDetailSerializer
        if self.action == 'place':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('customer', 'restaurant', 'driver').prefetch_related('menu_item')
        if user.user_type == 'customer':
            return qs.filter(customer__user=user)
        elif user.user_type == 'restaurant_owner':
            return qs.filter(restaurant__owner=user)
        elif user.user_type == 'delivery_driver':
            return qs.filter(driver__user=user)       
    
    @action(detail=False, methods=['post'], url_path='place', throttle_classes=[OrderCreateThrottle])
    def place(self, request, *args, **kwargs):
        if request.user.user_type != 'customer':
            return Response({'message': 'Only customers can place orders.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data, context={'request': request})
        print(serializer)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # web socket
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     f"restaurant_{order.restaurant.id}",
        #     {
        #         "type": "new_order",
        #         "order_id": str(order.order_number),
        #         "message": "New order received!"
        #     }
        # )
        return Response(OrderDetailSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request,  *args, **kwargs):
        order = self.get_object()
        user_type = request.user.user_type
        print(user_type)
        if user_type == 'delivery_driver':
            return Response({'error': 'Driver cannot cancel the order.'}, status=status.HTTP_400_BAD_REQUEST)
        if not order.can_cancel():
            return Response({'error': 'This order cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        #web socket
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"restaurant_{order.restaurant.id}",
            {
                "type": "order_status_update",
                "order_id": str(order.order_number),
                "status":order.status,
                "message": "Order cancelled!"
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"order_{order.order_number}",
            {
                "type": "order_status_update",
                "order_id": str(order.order_number),
                "status":order.status,
                "message": "Order cancelled!"
            }
        )

        return Response({'success': 'Order cancelled successfully.'})

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request,  *args, **kwargs):
        if request.user.user_type == 'customer':
            return Response({'message': 'Only Restaurants and Driver can update order status.'}, status=status.HTTP_403_FORBIDDEN)

        user_type = request.user.user_type
        order = self.get_object()
        new_status = request.data.get('status')

        if user_type == 'restaurant_owner':
            if new_status not in ['confirmed','preparing','ready']:
                return Response({'error': f'{new_status} status is not valid'})
            
            elif order.status == 'pending':
                if new_status != 'confirmed':
                    return Response({'error': f'Please confirm the order first.'})
                
            elif order.status == 'confirmed':
                if new_status != 'preparing':
                    return Response({'error': f'Please prepare the order first.'})
                
            elif order.status == 'preparing':
                if new_status != 'ready':
                    return Response({'error': f'Please ready the order first.'})

            else:
                return Response({'error': f'You can not do more actions.'})
            
        if user_type == 'delivery_driver':
            if new_status not in ['picked_up','delivered']:
                return Response({'error': f'{new_status} status is not valid'})

            elif order.status == 'ready':
                if new_status != 'picked_up':
                    return Response({'error': f'Please pick up the order first.'})
            
            elif order.status == 'picked_up':
                if new_status != 'delivered':
                    return Response({'error': f'Please deliver the order.'})

            else:
                return Response({'error': f'You can not do more actions.'})

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        if order.status == 'delivered':
            order.actual_delivery_time = timezone.localtime(timezone.now()).time()
            order.save(update_fields=['actual_delivery_time'])
            print(order.driver.id)
            driver = DriverProfile.objects.filter(id=order.driver.id).first()
            print(driver)
            driver.update_availability(True)
            driver.save()
    
        #web socket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"restaurant_{order.restaurant.id}",
            {
                "type": "order_status_update",
                "order_id": str(order.order_number),
                "status":order.status,
                "message": "Order status updated!"
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"order_{order.order_number}",
            {
                "type": "order_status_update",
                "order_id": str(order.order_number),
                "status":order.status,
                "message": "Order status updated!"
            }
        )
        
        if order.driver:
            async_to_sync(channel_layer.group_send)(
                f"driver_{order.driver.id}",
                {
                    "type": "order_status_update_driver",
                    "order_id": str(order.order_number),
                    "status":order.status,
                    "message": "Order status updated!"
                }
            )
        return Response({'success': f'Order status updated to {new_status}.'})

    # doubt maybe wrong logic
    @action(detail=True, methods=['post'], url_path='assign-driver')
    def assign_driver(self, request,  *args, **kwargs):
        order = self.get_object()
        if order.driver:
            return Response({'error': f'Driver is assigned. You cannot assign driver again'},400)
    
        try:
            driver = DriverProfile.objects.filter(is_available=True).first()
        except DriverProfile.DoesNotExist:
            return Response({'detail': 'Driver not found.'}, status=status.HTTP_404_NOT_FOUND)
        order.driver = driver
        driver.update_availability(False)
        driver.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                f"driver_{order.driver.id}",
                {
                    "type": "order_status_update_driver",
                    "order_id": str(order.order_number),
                    "status":order.status,
                    "message": "Order status updated!"
                }
            )
        
        async_to_sync(channel_layer.group_send)(
            f"order_{order.order_number}",
            {
                "type": "order_status_update",
                "order_id": str(order.order_number),
                "status":order.status,
                "message": "Order status updated!"
            }
        )

        order.save(update_fields=['driver', 'updated_at'])
        return Response({'detail': f'Driver assigned successfully.'})
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        return Response({'error':'You cannot delete the order'},status=status.HTTP_400_BAD_REQUEST)
    

class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return OrderItem.objects.filter(order__customer__user=user)
        elif user.user_type == 'restaurant_owner':
            return OrderItem.objects.filter(order__restaurant__owner=user)
        elif user.user_type == 'delivery_driver':
            return OrderItem.objects.filter(order__driver__user=user)
        return OrderItem.objects.none()


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = ReviewLimitOffsetPagination
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    ordering_fields = ['rating',]
    ordering = ['-created_at']

    def perform_create(self, serializer):
        customer_profile = self.request.user.customer_profile
        serializer.save(customer=customer_profile)
