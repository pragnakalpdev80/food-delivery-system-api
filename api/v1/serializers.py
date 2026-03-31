from rest_framework import serializers
from api.models import *
from api.validators import *


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
    default_address = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = ['user', 'avatar', 'total_orders', 'loyalty_points','default_address']
        read_only_fields = ['user', 'total_orders', 'loyalty_points']  

    def get_default_address(self, obj):
        print(obj)
        address = obj.default_address      
        if address:
            return AddressSerializer(address).data
        return None
    
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','address_name', 'address', 'is_default', 'user']
        read_only_fields = ['id','user']
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return Address.objects.create(**validated_data)
   

class DriverProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb], required=False)   
    delivery_stats = serializers.SerializerMethodField()

    class Meta:
        model = DriverProfile
        fields = ['user', 'avatar', 'vehicle_type', 'vehicle_number',
                  'license_number', 'is_available', 'total_deliveries', 'average_rating']
        read_only_fields = ['user', 'total_deliveries', 'average_rating']  

    def get_delivery_stats(self, obj):
        return obj.get_delivery_stats()
    
    
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


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu_items = serializers.SerializerMethodField()   
    # reviews = serializers.SerializerMethodField()        
    is_open_now = serializers.SerializerMethodField()            

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'name', 'description', 'cuisine_type', 'address',
                  'phone_no', 'email', 'logo', 'banner', 'opening_time',
                  'closing_time', 'is_open', 'is_open_now', 'delivery_fee', 'minimum_order',
                  'average_rating', 'total_reviews', 'menu_items']
        read_only_fields = ['average_rating', 'total_reviews', 'owner']

    def get_is_open_now(self, obj):
        print(obj)
        return obj.is_currently_open()
    
    def get_menu_items(self, obj):
        items = obj.menu_items.filter(is_available=True)
        return MenuItemSerializer(items, many=True).data

    # def get_reviews(self, obj):
    #     reviews = obj.reviews.all().order_by('-created_at')
    #     return ReviewSerializer(reviews, many=True).data


class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_image_format, validate_image_size_5mb], required=False) 
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_amount])

    class Meta:
        model = MenuItem
        fields = ['id', 'restaurant', 'name', 'description', 'price', 'category',
                  'dietary_info', 'image', 'is_available', 'preparation_time']
        read_only_fields = ['restaurant','id']

    def create(self, validated_data):
        request = self.context.get('request')
        restaurant = Restaurant.objects.get(owner = request.user)
        validated_data['restaurant'] = restaurant
        return MenuItem.objects.create(**validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'customer', 'restaurant', 'menu_item', 'order', 'rating', 'comment']  
        read_only_fields = ['customer']  


class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_price = serializers.DecimalField(
        source='menu_item.price', max_digits=8, decimal_places=2, read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'menu_item_name', 'menu_item_price',
                  'quantity', 'special_instructions', 'subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()

    def validate_menu_item(self, value):
        request = self.context.get('request')
        try:
            cart = request.user.customer_profile.cart
        except (AttributeError, Cart.DoesNotExist):
            return value                  
        if cart.restaurant and value.restaurant != cart.restaurant:
            raise serializers.ValidationError(
                f"Clear your cart first."
            )
        return value


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'restaurant', 'restaurant_name',
                  'cart_items', 'total', 'item_count']
        read_only_fields = ['customer', 'restaurant']

    def get_total(self, obj):
        return obj.get_total()

    def get_item_count(self, obj):
        return obj.cart_items.count()


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
    # delivery_address = serializers.SerializerMethodField()

    # def get_delivery_address(self, obj):
    #     request = self.context.get('request')
    #     qs = Address.objects.filter(user=request.user,is_default=True)
    #     print(qs)
    #     serializer = AddressSerializer(qs, many=True)
    #     return serializer.data

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'driver', 'order_number',   
                  'status', 'delivery_address', 'subtotal', 'delivery_fee',
                  'tax', 'total_amount', 'special_instructions',
                  'estimated_delivery_time', 'actual_delivery_time']
        read_only_fields = ['customer', 'order_number', 'subtotal', 'delivery_fee',
                            'tax', 'total_amount', 'estimated_delivery_time', 'actual_delivery_time']


class OrderDetailSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    menu_item = OrderItemSerializer(read_only=True, many=True)  
    can_cancel = serializers.SerializerMethodField()         
    is_delivered = serializers.SerializerMethodField()       

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'driver', 'order_number', 'status',
                  'delivery_address', 'subtotal', 'delivery_fee', 'tax', 'total_amount',
                  'special_instructions', 'estimated_delivery_time', 'actual_delivery_time',
                  'menu_item', 'can_cancel', 'is_delivered']
        read_only_fields = ['customer', 'order_number', 'subtotal', 'delivery_fee',
                            'tax', 'total_amount', 'estimated_delivery_time', 'actual_delivery_time']

    def get_can_cancel(self, obj):
        return obj.can_cancel()

    def get_is_delivered(self, obj):
        return obj.is_delivered() 

