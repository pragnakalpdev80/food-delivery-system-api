from rest_framework import serializers
from api.models import User,CustomerProfile, DriverProfile,Restaurant, MenuItem, Order, OrderItem ,Review
from api.validators import validate_image_format, validate_image_size_5mb, validate_image_size_10mb

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8,style = {'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True,style = {'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password',
                  'first_name', 'last_name','phone_no','user_type',]
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        user.save()
        return user

class CustomerProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(validators=[validate_image_format,validate_image_size_5mb])
    class Meta:
        model = CustomerProfile
        fields = ['user','avatar','default_address','saved_addresses',
                  'total_orders','loyalty_points',]
        read_only_fields = ['total_orders','loyalty_points',]

class DriverProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb])
    class Meta:
        model = DriverProfile
        fields = ['user','avatar','vehicle_type','vehicle_number',
                  'license_number','is_available','total_deliveries',
                  'average_rating',]
        read_only_fields = ['total_deliveries','average_rating']

class RestaurantSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb])
    banner = serializers.ImageField(validators=[validate_image_format, validate_image_size_10mb])
    class Meta:
        model = Restaurant
        fields = ['owner','name','description','cuisine_type','address',
                  'phone_no','email','logo','banner','opening_time',
                  'closing_time','is_open','delivery_fee','minimum_order',
                  'average_rating','total_reviews']
        read_only_fields = ['average_rating','total_reviews']

class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb])
    restaurant = RestaurantSerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['restaurant','name','description','price','category',
                  'dietary_info','image','is_available','preparation_time']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer','restaurant','driver','order_number',
                  'status','delivery_address','subtotal','delivery_fee',
                  'tax','total_amount','special_instructions',
                  'estimated_delivery_time','actual_delivery_time',]
        read_only_fields = ['order_number','estimated_delivery_time','actual_delivery_time']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order','menu_item','quantity','price','special_instructions',]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['customer','restaurant','menu_item','order',
                  'rating','comment',]

class OrderDetailSerializer(serializers.ModelField):
    restaurant = RestaurantSerializer(read_only=True)
    customer = CustomerProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['customer','restaurant''driver','order_number','status',
                  'delivery_address','subtotal','delivery_fee','tax','total_amount',
                  'special_instructions','estimated_delivery_time','actual_delivery_time',]
        read_only_fields= ['customer','restaurant','driver',]

class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    item_review = ReviewSerializer(read_only=True)
    
    class Meta:
        model = Restaurant
        fields = ['owner','name','description','cuisine_type','address',
                  'phone_no','email','logo','banner','opening_time',
                  'closing_time','is_open','delivery_fee','minimum_order',
                  'average_rating','total_reviews','menu_item','item_review']
        read_only_fields = ['average_rating','total_reviews']
