from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from api.models import User
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, CustomerProfileSerializer, DriverProfileSerializer,RestaurantSerializer,MenuItemSerializer,OrderItemSerializer,OrderSerializer,ReviewSerializer,RestaurantDetailSerializer,OrderDetailSerializer
from api.pagination import RestaurantPageNumberPagination, OrderCursorPagination, MenuItemPageNumberPagination, ReviewLimitOffsetPagination
from api.filters import RestaurantFilter, MenuItemFilter, OrderFilter, ReviewFilter
from api.models import User,CustomerProfile, DriverProfile,Restaurant, MenuItem, Order, OrderItem ,Review
from api.permissions import IsOwnerOrReadOnly, IsOrderCustomer, IsCustomer, IsDriver, IsRestaurantOwner, IsRestaurantOwnerOrDriver, IsRestaurantOwnerOrReadOnly
from api.throttles import LocationUpdateThrottle, OrderCreateThrottle, ReviewCreateThrottle

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
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsRestaurantOwnerOrReadOnly]
    pagination_class = RestaurantPageNumberPagination
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    filterset_class = RestaurantFilter
    search_fields = ['name', 'cuisine_type', 'description']
    ordering_fields = ['-average_rating', 'delivery_fee', 'created_at',]
    ordering = ['-created_at']

class MenuItemViewSet(viewsets.ModelViewSet):
    permission_classes = []
    pagination_class =MenuItemPageNumberPagination
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at',]
    ordering = ['-created_at']

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class =OrderCursorPagination
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['total_amount',]
    ordering = ['-created_at']
    # queryset = Order.objects.all()

    def get_queryset(self):
        if self.request.user.user_type == 'customer':
            x = list(CustomerProfile.objects.filter(user_id = self.request.user.id).values_list("id", flat=True))
            return Order.objects.filter(customer_id = x[0])
        
        elif self.request.user.user_type == 'restaurant_owner':
            x = list(Restaurant.objects.filter(user_id = self.request.user.id).values_list("id", flat=True))
            return Order.objects.filter(owner_id = x[0])
        
        elif self.request.user.user_type == 'delivery_driver':
            x = list(DriverProfile.objects.filter(user_id = self.request.user.id).values_list("id", flat=True))
            return Order.objects.filter(driver_id = x[0])
    
    @action(detail=False, methods=['post'], url_path='place', throttle_classes=[OrderCreateThrottle])
    def place(self, request, *args, **kwargs):
        if request.user.user_type != 'customer':
            return Response({'message': 'Only customers can place orders.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderDetailSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = ReviewLimitOffsetPagination
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    ordering_fields = ['rating',]
    ordering = ['-created_at']