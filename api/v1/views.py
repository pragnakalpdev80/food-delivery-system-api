import logging
from django.utils import timezone
from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import (
    UserRegistrationSerializer,
    CustomerProfileSerializer,
    AddressSerializer,
    DriverProfileSerializer,
    RestaurantSerializer,
    RestaurantDetailSerializer,
    MenuItemSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderDetailSerializer,
    OrderItemSerializer,
    ReviewSerializer
)
from api.pagination import (
    MenuItemPageNumberPagination,
    ReviewLimitOffsetPagination,
    RestaurantPageNumberPagination,
    OrderCursorPagination
)
from api.filters import (
    ReviewFilter,
    MenuItemFilter,
    OrderFilter,
    RestaurantFilter
)
from api.models import (
    User, CustomerProfile, DriverProfile, 
    Restaurant, Address, MenuItem, Cart, 
    CartItem, Order, OrderItem, Review
)
from .permissions import (
    IsOwnerOrReadOnly,
    IsCustomer,
    IsDriver,
    IsOrderCustomer,
    IsRestaurantOwner,
    IsRestaurantOwnerOrDriver
)
from api.throttles import (
    OrderCreateThrottle,
    ReviewCreateThrottle,
)

logger = logging.getLogger(__name__)

@extend_schema_view(
    post=extend_schema(
        summary="Registration",
        description=" Endpoint for new user registration of all types.",
        tags=["Userbase"],
        request=UserRegistrationSerializer,
        responses={
            201:UserRegistrationSerializer,
            400:{}
        }
    )
)
class UserRegistrationView(generics.CreateAPIView):
    """ User registration view to create/update and delete new user. """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create method to create user and it will return user's data and refresh and access token.
        """
        serializer = self.get_serializer(data=request.data)   
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,  
            'refresh': str(refresh),  
            'access': str(refresh.access_token),  
        }, status=status.HTTP_201_CREATED)  


@extend_schema_view(
    create=extend_schema(
        summary="This method is not allowed",
        description = "Customer profile creates automatically upon user creation",
        tags=['Customer Profile']
    ),
    list=extend_schema(
        summary=" Customer Profile",
        description="Customer profile",
        responses={
            200:CustomerProfileSerializer
        },
        tags=["Customer Profile"]),
    retrieve=extend_schema(
        summary=" Customer Profile",
        description="Customer profile details",
        responses={
            200:CustomerProfileSerializer
        },
        tags=["Customer Profile"]),
    partial_update=extend_schema(
        summary="Update Customer Profile",
        description=" Update your profile details here",
        request=CustomerProfileSerializer,
        responses={
            200:CustomerProfileSerializer
        },
        tags=['Customer Profile']
    ),
    destroy=extend_schema(
        summary="Customer Profile",
        description = "We have added soft delete to delete customer profile",
        tags=['Customer Profile']
    ),
)
class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer Viewset to manage customer profile.
    """
    permission_classes = [IsAuthenticated,IsCustomer]
    serializer_class = CustomerProfileSerializer
    http_method_names = ['get', 'post', 'patch','delete']

    def get_queryset(self):
        """ Queryset to get customer can only access own profile. """
        if not self.request.user.is_authenticated:
            return CustomerProfile.objects.none()
        return CustomerProfile.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """ Method to soft delete the customer. """
        instance.is_deleted = True
        instance.save()

@extend_schema_view(
    create=extend_schema(
        summary="Customer Address",
        description = "Customer Address creation",
        tags=['Customer Address']
    ),
    list=extend_schema(
        summary="Customer Address",
        description="Customer Addresses",
        tags=["Customer Address"]),
    retrieve=extend_schema(
        summary="Customer Address",
        description="Customer Address details",
        tags=["Customer Address"]),
    partial_update=extend_schema(
        summary="Update Customer Address",
        description=" Update your Address details here",
        tags=['Customer Address']
    ),
    destroy=extend_schema(
        summary="Soft deletion of customer address",
        description = "We have added soft delete to delete customer address",
        tags=['Customer Address']
    ),
)
class AddressViewSet(viewsets.ModelViewSet):
    """
    Customer Viewset to manage customer addresses.
    """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = AddressSerializer
    http_method_names = ['get', 'post', 'patch','delete']

    def get_queryset(self):
        """ Only customers can manage own addresses only"""
        if not self.request.user.is_authenticated:
            return Address.objects.none()
        return Address.objects.filter(user = self.request.user,is_deleted=False)
    
    def perform_destroy(self, instance):
        """ Method to soft delete the address. """
        instance.is_deleted = True
        instance.save()

@extend_schema_view(
    create=extend_schema(
        summary="This method is not allowed",
        description = "CusDrivertomer profile creates automatically upon user creation",
        tags=['Driver Profile']
    ),
    list=extend_schema(
        summary="Driver Profile",
        description="Driver profile",
        tags=["Driver Profile"]),
    retrieve=extend_schema(
        summary="Driver Profile",
        description="Driver profile details",
        tags=["Driver Profile"]),
    partial_update=extend_schema(
        summary="Update Driver Profile",
        description=" Update your profile details here",
        tags=['Driver Profile']
    ),
    destroy=extend_schema(
        summary="Driver Profile",
        description = "We have added soft delete to delete driver profile",
        tags=['Driver Profile']
    ),
)
class DriverViewSet(viewsets.ModelViewSet):
    """ Driver ViewSet to manage driver's profile. """
    permission_classes = [IsAuthenticated, IsDriver]
    serializer_class = DriverProfileSerializer
    http_method_names = ['get', 'post', 'patch','delete']

    def get_queryset(self):
        """ Queryset to get drivers can only access own profile. """
        if not self.request.user.is_authenticated:
            return DriverProfile.objects.none()
        return DriverProfile.objects.filter(user=self.request.user,is_deleted=False)

    def perform_destroy(self, instance):
        """ Method to soft delete the driver profile. """
        instance.is_deleted = True
        instance.save()

@extend_schema_view(
    create=extend_schema(
        summary="Restaurant",
        description = "Restaurant creation",
        tags=['Restaurant']
    ),
    list=extend_schema(
        summary="Restaurant",
        description="Restaurants",
        tags=["Restaurant"]
    ),
    retrieve=extend_schema(
        summary="Restaurant",
        description="Restaurant details",
        tags=["Restaurant"]
    ),
    partial_update=extend_schema(
        summary="Update Restaurant Details",
        description=" Update your Restaurant details here",
        tags=['Restaurant']
    ),
    destroy=extend_schema(
        summary="Restaurant",
        description = "We have added soft delete to delete Restaurant",
        tags=['Restaurant']
    ),
    menu=extend_schema(
        summary="Restaurant",
        description = "Restaurant Menu",
        tags=['Restaurant']
    ),
    popular=extend_schema(
        summary="Restaurant",
        description = "Popular Restaurants",
        tags=['Restaurant']
    ),
)
class RestaurantViewSet(viewsets.ModelViewSet):
    """ Driver ViewSet to manage restaurants. """
    permission_classes = [IsAuthenticated, IsRestaurantOwner, IsOwnerOrReadOnly]
    pagination_class = RestaurantPageNumberPagination
    queryset = Restaurant.objects.filter(is_deleted=False)
    serializer_class = RestaurantDetailSerializer
    filterset_class = RestaurantFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name', 'cuisine_type', 'description']
    ordering_fields = ['-average_rating', 'delivery_fee', 'created_at',]
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'patch','delete']
    
    def get_permissions(self):
        """
        Only restaurant owner can create, update and delete others can only see the details.
        """
        if self.action in ['list', 'retrieve', 'menu', 'popular']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsRestaurantOwner(), IsOwnerOrReadOnly()]

    def get_serializer_class(self):
        """
        When user searches for specific request then it will show the restaurant with menu items
        and for other methods it will show only restaurant details only.
        """
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantSerializer

    def perform_destroy(self, instance):
        """ Method to soft delete the restaurant. """
        instance.is_deleted = True
        instance.save()

    @method_decorator(cache_page(60 * 5), name='list_restaurant')
    def list(self, request, *args, **kwargs):
        """ Overriden list method to get pagination on restaurants and added 5 minutes. """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RestaurantSerializer(self.filter_queryset(self.get_queryset()), many=True, context={"request": request})
        return Response(serializer.data)
    
    @method_decorator(cache_page(60 * 10), name='retrieve_restaurant')
    def retrieve(self, request, *args, **kwargs):
        """ Added cache of 10 minutes on restaurant details method. """
        return super().retrieve(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15), name='restaurant_menu')
    @action(detail=True, methods=['get'], url_path='menu')
    def menu(self, request,  *args, **kwargs):
        """ Created a custom menu method to get menu of the restaurant with 15 minutes of cache. """
        restaurant = self.get_object()
        items = MenuItem.objects.filter(restaurant_id=restaurant.id, is_available=True)
          # print(items)
        serializer = MenuItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request,  *args, **kwargs):
        """ Created a custom method to get popular restaurants and added 30 minutes of cache on the method. """
        cache_key = 'popular_restaurant'
        cached_data = cache.get(cache_key)
        logger.info(cached_data)
        if cached_data is None:
            popular = Restaurant.objects.filter(is_open=True).order_by('-average_rating')
            serializer = RestaurantSerializer(popular, many=True, context={'request': request})
            cached_data = serializer.data
            cache.set(cache_key, cached_data, 1800)
        return Response(cached_data,status=status.HTTP_200_OK)
    
    

@extend_schema_view(
    create=extend_schema(
        summary="Menu Items",
        description = "Menu Items creation",
        tags=['Menu Items']
    ),
    list=extend_schema(
        summary="Menu Items",
        description="Menu Item",
        tags=["Menu Items"]
    ),
    retrieve=extend_schema(
        summary="Menu Items",
        description="Menu Item details",
        tags=["Menu Items"]
    ),
    partial_update=extend_schema(
        summary="Update Menu Items",
        description=" Update your menu items details here",
        tags=['Menu Items']
    ),
    destroy=extend_schema(
        summary="Menu Items",
        description = "We have added soft delete to delete Menu Items",
        tags=['Menu Items']
    ),
)
class MenuItemViewSet(viewsets.ModelViewSet):
    """ Menu items ViewSet to manage the menu items of restaurant. """
    pagination_class =MenuItemPageNumberPagination
    # queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at',]
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'patch','delete']

    def get_permissions(self):
        """
        Permissions for authenticated users can see restaurants menu items and only restaurant owners can access all routes.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsRestaurantOwner(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        """
        Owners can create, update and delete own restaurants items.
        """
        if not self.request.user.is_authenticated:
            return MenuItem.objects.none()
        user = self.request.user
        if user.user_type == 'restaurant_owner':
            return MenuItem.objects.filter(restaurant__owner=user,is_deleted=False).select_related('restaurant')
        return MenuItem.objects.filter(is_available=True,is_deleted=False).select_related('restaurant')

    def perform_destroy(self, instance):
        """ Method to soft delete the menu items. """
        instance.is_deleted = True
        instance.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete_many(['list_restaurant','retrieve_restaurant','restaurant_menu'])
        return response
    
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        cache.delete_many(['list_restaurant','retrieve_restaurant','restaurant_menu'])
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.delete_many(['list_restaurant','retrieve_restaurant','restaurant_menu'])
        return response
    

@extend_schema_view(
    list=extend_schema(
        summary="Restaurant",
        description="Restaurants",
        tags=["Cart"]
    ),
    retrieve=extend_schema(
        summary="Cart",
        description="Cart details",
        tags=["Cart"]
    ),
    destroy=extend_schema(
        summary="This method is not allowed",
        description = "Customer cannot delete cart.",
        tags=['Cart']
    ),
    clear=extend_schema(
        summary="Clear the Cart",
        description = "Remove items from the cart.",
        tags=['Cart']
    ),
)
class CartViewSet(viewsets.ModelViewSet):
    """ Cart ViewSet to manage the cart of customers. """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CartSerializer
    http_method_names = ['get','delete']

    def get_queryset(self):
        """
        Customers can only access their own cart only.
        """
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.prefetch_related('cart_items', 'cart_items__menu_item').filter(customer=self.request.user.customer_profile)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """
        Method to remove all cart items from the cart.
        """
        try:
            cart = request.user.customer_profile.cart
            cart.cart_items.all().delete()
            cart.restaurant = None
            cart.save(update_fields=['restaurant', 'updated_at'])
        except Cart.DoesNotExist:
            pass
        return Response({'success': 'Cart cleared.'},status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """ Cart creation endpoint is bloacked beacause when a customer will register then customer's cart will be created automatically and every customer can have only one cart."""
        return Response({'error':'User can only have one cart'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@extend_schema_view(
    create=extend_schema(
        summary="Cart Item",
        description = "Cart Item creation",
        tags=['Cart Item']
    ),
    list=extend_schema(
        summary="Cart Item",
        description="Cart Items",
        tags=["Cart Item"]
    ),
    retrieve=extend_schema(
        summary="Cart Item",
        description="Cart Item details",
        tags=["Cart Item"]
    ),
    partial_update=extend_schema(
        summary="Update Cart Item",
        description=" Update your Cart Items here.",
        tags=['Cart Item']
    ),
    destroy=extend_schema(
        summary="Cart Item",
        description = "Remove item from the cart.",
        tags=['Cart Item']
    ),
)
class CartItemViewSet(viewsets.ModelViewSet):
    """ Cart ViewSet to manage the cart of customers. """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'patch','delete']

    def get_queryset(self):
        """ customers can only acccess their own cart items only. """
        if not self.request.user.is_authenticated:
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__customer=self.request.user.customer_profile).select_related('menu_item')
    

@extend_schema_view(
    create=extend_schema(
        summary="This method is not allowed",
        description = "You can create order via place method.",
        tags=['Order']
    ),
    list=extend_schema(
        summary="Order",
        description="Order",
        tags=["Order"]
    ),
    retrieve=extend_schema(
        summary="Order",
        description="Order details",
        tags=["Order"]
    ),
    update_status=extend_schema(
        summary="Order Status Update",
        description = "Order Status Update.",
        tags=['Order']
    ),
    assign_driver=extend_schema(
        summary="Driver Assign to Order",
        description = "Assign the driver to the order.",
        tags=['Order']
    ),
    cancel=extend_schema(
        summary="Cancel Order",
        description = "Customer can cancel the order if it is not preapared.",
        tags=['Order']
    ),
    place=extend_schema(
        summary="Place Order",
        description = "Customers can place orders from here.",
        tags=['Order']
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """ Order ViewSet to manage the order of customers. """
    permission_classes = [IsAuthenticated]
    pagination_class =OrderCursorPagination
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['order_number']
    ordering_fields = ['total_amount',]
    ordering = ['-created_at']
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        """ Different serializers for different method as per required fields. """
        if self.action in ['retrieve']:
            return OrderDetailSerializer
        if self.action == 'place':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_permissions(self):
        """
        Permissions for different actions.
        """
        if self.action in ['place', 'cancel']:
            return [IsAuthenticated(), IsCustomer()]
        if self.action in ['assign-driver', 'cancel']:
            return [IsAuthenticated(), IsRestaurantOwner(), IsOwnerOrReadOnly()]
        if self.action in ['update-status']:
            return [IsRestaurantOwnerOrDriver]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Customers can see thier own orders.
        Restaurant owners can see restaurants orders only.
        delivery drivers can see assigned orders only.
        """
        user = self.request.user
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        qs = Order.objects.select_related('customer', 'restaurant', 'driver').prefetch_related('menu_item')
        if user.user_type == 'customer':
            return qs.filter(customer__user=user)
        elif user.user_type == 'restaurant_owner':
            return qs.filter(restaurant__owner=user)
        elif user.user_type == 'delivery_driver':
            return qs.filter(driver__user=user)       
    
    @action(detail=False, methods=['post'], url_path='place', throttle_classes=[OrderCreateThrottle])
    def place(self, request, *args, **kwargs):
        """
        Custom method to place the order
        """
        if request.user.user_type != 'customer':
            return Response({'message': 'Only customers can place orders.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data, context={'request': request})
          # print(serializer)
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
        """
        Custom method to cancel the order.
        """
        order = self.get_object()
        user_type = request.user.user_type
         # print(user_type)
        if user_type == 'delivery_driver':
            return Response({'error': 'Driver cannot cancel the order.'}, status=status.HTTP_400_BAD_REQUEST)
        if not order.can_cancel():
            return Response({'error': 'This order cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        if order.driver:
            driver = DriverProfile.objects.filter(id=order.driver.id).first()
             # print(driver)
            driver.update_availability(True)
            driver.save(update_fields=['updated_at','is_available'])
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

        async_to_sync(channel_layer.group_send)(
            f"customer_{order.customer.id}",
            {
                "type": "order_status_update",
                "order_id": str(order.order_number),
                "status":order.status,
                "message": "Order cancelled!"
            }
        )

        return Response({'success': 'Order cancelled successfully.'},status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request,  *args, **kwargs):
        """
        Custom method to update the order status
        """
        if request.user.user_type == 'customer':
            return Response({'message': 'Only Restaurants and Driver can update order status.'}, status=status.HTTP_403_FORBIDDEN)

        user_type = request.user.user_type
        order = self.get_object()
        new_status = request.data.get('status')

        if user_type == 'restaurant_owner':
            if new_status not in ['confirmed','preparing','ready']:
                return Response({'error': f'{new_status} status is not valid'},status=status.HTTP_400_BAD_REQUEST)
            
            elif order.status == 'pending':
                if new_status != 'confirmed':
                    return Response({'error': f'Please confirm the order first.'},status=status.HTTP_400_BAD_REQUEST)
                
            elif order.status == 'confirmed':
                if new_status != 'preparing':
                    return Response({'error': f'Please prepare the order first.'},status=status.HTTP_400_BAD_REQUEST)
                
            elif order.status == 'preparing':
                if new_status != 'ready':
                    return Response({'error': f'Please ready the order first.'},status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': f'You can not do more actions.'},status=status.HTTP_400_BAD_REQUEST)
            
        if user_type == 'delivery_driver':
            if new_status not in ['picked_up','delivered']:
                return Response({'error': f'{new_status} status is not valid'},status=status.HTTP_400_BAD_REQUEST)

            elif order.status == 'ready':
                if new_status != 'picked_up':
                    return Response({'error': f'Please pick up the order first.'},status=status.HTTP_400_BAD_REQUEST)
            
            elif order.status == 'picked_up':
                if new_status != 'delivered':
                    return Response({'error': f'Please deliver the order.'},status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': f'You can not do more actions.'},status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        if order.status == 'delivered':
            order.actual_delivery_time = datetime.now()
            order.save(update_fields=['actual_delivery_time'])
              # print(order.driver.id)
            driver = DriverProfile.objects.filter(id=order.driver.id).first()
              # print(driver)
            driver.update_availability(True)
            driver.save(update_fields=['updated_at','is_available'])
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
        return Response({'success': f'Order status updated to {new_status}.'},status=status.HTTP_200_OK)

    # doubt maybe wrong logic
    @action(detail=True, methods=['post'], url_path='assign-driver')
    def assign_driver(self, request,  *args, **kwargs):
        """
        Custom method to assign the driver to order.
        """
        order = self.get_object()
        if order.driver:
            return Response({'error': f'Driver is assigned. You cannot assign driver again'},status=status.HTTP_400_BAD_REQUEST)
    
        try:
            driver = DriverProfile.objects.filter(is_available=True).first()
            if not driver:
                return Response({'detail': 'No available driver found.'}, status=status.HTTP_404_NOT_FOUND)
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
        return Response({'detail': f'Driver assigned successfully.'},status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Create method is blocked because we are allowing to order from the cart only.
        """
        return Response({'error':'You cannot create orders directly use place method to create orders'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
 
 
@extend_schema_view(
    create=extend_schema(
        summary="This method is not allowed",
        description="Customer cannot create order items",
        tags=['Order Item']
    ),
    list=extend_schema(
        summary="Order Item",
        description="Order Items",
        tags=["Order Item"]
    ),
    retrieve=extend_schema(
        summary="Order Item",
        description="Order Item details",
        tags=["Order Item"]
    ),
)
class OrderItemViewSet(viewsets.ModelViewSet):
    """ Order items ViewSet to see the order items of customers. """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    http_method_names = ['get']

    def get_queryset(self):
        """
        Customers can see thier own order's items only.
        Restaurant owners can see restaurants order's items only.
        delivery drivers can see assigned order's items only.
        """
        user = self.request.user
        if not self.request.user.is_authenticated:
            return OrderItem.objects.none()
        if user.user_type == 'customer':
            return OrderItem.objects.filter(order__customer__user=user)
        elif user.user_type == 'restaurant_owner':
            return OrderItem.objects.filter(order__restaurant__owner=user)
        elif user.user_type == 'delivery_driver':
            return OrderItem.objects.filter(order__driver__user=user)
        return OrderItem.objects.none()

    def create(self, request, *args, **kwargs):
        """
        User cannot add items only via cart users can create.
        """
        return Response({'error':'Please order via Cart'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    
    def partial_update(self, request, *args, **kwargs):
        """
        User cannot update the order items.
        """
        return Response({'error':'You cannot update order items'},status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema_view(
    create=extend_schema(
        summary="Review",
        description = "Review creation",
        tags=['Review']
    ),
    list=extend_schema(
        summary="Review",
        description="Reviews",
        tags=["Review"]
    ),
    retrieve=extend_schema(
        summary="Review",
        description="Review details",
        tags=["Review"]
    ),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """ Reveiw ViewSet to manage to reviews. """
    permission_classes = [IsAuthenticated, IsOrderCustomer]
    pagination_class = ReviewLimitOffsetPagination
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['rating',]
    ordering = ['-created_at']
    throttle_classes = [ReviewCreateThrottle]
    http_method_names = ['get', 'post']

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete_many(['list_restaurant','retrieve_restaurant'])
        return response
    
    def perform_create(self, serializer):
        """ Customer can only review their own orders only. """
        customer_profile = self.request.user.customer_profile
        serializer.save(customer=customer_profile)

    def partial_update(self, request, *args, **kwargs):
        """
        User cannot update reviews.
        """
        return Response({'error':'You cannot update order items'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    