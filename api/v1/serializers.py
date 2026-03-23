from rest_framework import serializers
from api.models import User, CustomerProfile, DriverProfile, Restaurant, MenuItem, Order, OrderItem, Review
from api.validators import validate_image_format, validate_image_size_5mb, validate_image_size_10mb, validate_amount


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password',
                  'first_name', 'last_name', 'phone_no', 'user_type']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class CustomerProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb], required=False)  

    class Meta:
        model = CustomerProfile
        fields = ['user', 'avatar', 'default_address', 'saved_addresses',
                  'total_orders', 'loyalty_points']
        read_only_fields = ['user', 'total_orders', 'loyalty_points']  


class DriverProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb], required=False)   

    class Meta:
        model = DriverProfile
        fields = ['user', 'avatar', 'vehicle_type', 'vehicle_number',
                  'license_number', 'is_available', 'total_deliveries', 'average_rating']
        read_only_fields = ['user', 'total_deliveries', 'average_rating']  

class RestaurantSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb], required=False)    
    banner = serializers.ImageField(validators=[validate_image_format, validate_image_size_10mb], required=False)  
    delivery_fee = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_amount])
    minimum_order = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_amount])

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'name', 'description', 'cuisine_type', 'address',   
                  'phone_no', 'email', 'logo', 'banner', 'opening_time',
                  'closing_time', 'is_open', 'delivery_fee', 'minimum_order',
                  'average_rating', 'total_reviews']
        read_only_fields = ['average_rating', 'total_reviews', 'owner']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return Restaurant.objects.create(**validated_data)


class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb], required=False) 
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())
    restaurant_detail = RestaurantSerializer(source='restaurant', read_only=True)  
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_amount])

    class Meta:
        model = MenuItem
        fields = ['id', 'restaurant', 'restaurant_detail', 'name', 'description', 'price', 'category',
                  'dietary_info', 'image', 'is_available', 'preparation_time']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'price', 'special_instructions']   


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['restaurant', 'delivery_address', 'special_instructions', 'items']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'driver', 'order_number',   
                  'status', 'delivery_address', 'subtotal', 'delivery_fee',
                  'tax', 'total_amount', 'special_instructions',
                  'estimated_delivery_time', 'actual_delivery_time']
        read_only_fields = ['customer', 'order_number', 'subtotal', 'delivery_fee',
                            'tax', 'total_amount', 'estimated_delivery_time', 'actual_delivery_time']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'customer', 'restaurant', 'menu_item', 'order', 'rating', 'comment']  
        read_only_fields = ['customer']  



class OrderDetailSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)  
    can_cancel = serializers.SerializerMethodField()         
    is_delivered = serializers.SerializerMethodField()       

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'driver', 'order_number', 'status',
                  'delivery_address', 'subtotal', 'delivery_fee', 'tax', 'total_amount',
                  'special_instructions', 'estimated_delivery_time', 'actual_delivery_time',
                  'items', 'can_cancel', 'is_delivered']
        read_only_fields = ['customer', 'order_number', 'subtotal', 'delivery_fee',
                            'tax', 'total_amount', 'estimated_delivery_time', 'actual_delivery_time']

    def get_can_cancel(self, obj):
        return obj.can_cancel()

    def get_is_delivered(self, obj):
        return obj.is_delivered()


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)   
    reviews = ReviewSerializer(many=True, read_only=True)        
    is_open_now = serializers.SerializerMethodField()            

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'name', 'description', 'cuisine_type', 'address',
                  'phone_no', 'email', 'logo', 'banner', 'opening_time',
                  'closing_time', 'is_open', 'is_open_now', 'delivery_fee', 'minimum_order',
                  'average_rating', 'total_reviews', 'menu_items', 'reviews']
        read_only_fields = ['average_rating', 'total_reviews', 'owner']

    def get_is_open_now(self, obj):
        return obj.is_currently_open()

