from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from api.models import User
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, CustomerProfileSerializer, DriverProfileSerializer,RestaurantSerializer,MenuItemSerializer,OrderItemSerializer,OrderSerializer,ReviewSerializer,RestaurantDetailSerializer,OrderDetailSerializer
from api.pagination import RestaurantPageNumberPagination, OrderCursorPagination, MenuItemPageNumberPagination, ReviewLimitOffsetPagination
from api.filters import RestaurantFilter, MenuItemFilter, OrderFilter, ReviewFilter
from api.models import User,CustomerProfile, DriverProfile,Restaurant, MenuItem, Order, OrderItem ,Review


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
    permission_classes = []
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    permission_classes = []
    pagination_class = RestaurantPageNumberPagination
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
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
    permission_classes = []
    pagination_class =OrderCursorPagination
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['total_amount',]
    ordering = ['-created_at']

class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = []
    pagination_class = ReviewLimitOffsetPagination
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    ordering_fields = ['rating',]
    ordering = ['-created_at']