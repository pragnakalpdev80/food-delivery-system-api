import uuid
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email")

        email = self.normalize_email(email).lower()

        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        return user


    def create_superuser(self, email, password, **extra_fields):
        if not password:
            raise ValueError("Password is required")

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class TimestampedModel(models.Model):
    """Base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True 

class User(AbstractUser,TimestampedModel):
   USER_TYPE_CHOICES = (
        ('customer',"Customer"),('restaurant_owner',"Restaurant Owner"),('delivery_driver',"Delivery Driver"),
    )   
   phone_no = models.CharField(max_length = 10)
   user_type = models.CharField(choices=USER_TYPE_CHOICES)

   objects = UserManager()
   
   def __str__(self):
       return "{}".format(self.username)

class CustomerProfile(TimestampedModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='customer_avatar')
    default_address =models.TextField()
    saved_addresses = models.JSONField(default={'default':'1'})
    total_orders = models.IntegerField(default=0)
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
       return "{}".format(self.user)

class DriverProfile(TimestampedModel):

    VEHICLE_CHOICES = (
        ('bike',"Bike"),('scooter',"Scooter"),('car',"Car"),
    )   

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='driver_avatar')
    vehicle_type = models.CharField(choices=VEHICLE_CHOICES)
    vehicle_number = models.CharField()
    license_number =  models.CharField()
    is_available = models.BooleanField(default=True)
    total_deliveries = models.IntegerField(default=0)
    average_rating  = models.DecimalField(default=0,max_digits=10 ,decimal_places=2)

    def __str__(self):
       return "{}".format(self.user)

    def update_availability(self, status):
        self.is_available = status
        self.save(update_fields=['is_available', 'updated_at'])

    def get_delivery_stats(self):
        return {
            'total_deliveries': self.total_deliveries,
            'average_rating':   self.average_rating,
        }

class Restaurant(TimestampedModel):

    CUISINE_CHOICES =  (
        ("italian","Italian"), ("chinise","Chinese"), ("indian","Indian"), ("mexican","Mexican"), 
        ("american","American"), ("japanese","Japanese"), ("thai","Thai"), ("mediterranean","Mediterranean")
    )
    owner = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    cuisine_type = models.CharField(choices=CUISINE_CHOICES)
    address =models.TextField()
    phone_no = models.CharField(max_length = 10)
    email = models.EmailField()
    logo = models.ImageField(default='default.jpg', upload_to='restaurant_logo')
    banner = models.ImageField(default='default.jpg', upload_to='restaurant_banner')
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_open = models.BooleanField()
    delivery_fee = models.DecimalField(max_digits=10 ,decimal_places=2)
    minimum_order = models.DecimalField(default=0,max_digits=10 ,decimal_places=2)
    average_rating = models.DecimalField(default=0,max_digits=10 ,decimal_places=2)
    total_reviews = models.IntegerField(default=0)

    def __str__(self):
       return "{}".format(self.name)
    
    def is_currently_open(self):
        if datetime.now().strftime("%H:%M:%S")>self.opening_time or datetime.now().strftime("%H:%M:%S")<self.closing_time:
            return True
        return False
    
    # def update_average_rating(self):
    #     pass

class MenuItem(TimestampedModel):

    CATEGORY_CHOICES = (
        ("appetizer","Appetizer"), ("main_course","Main Course"), ("dessert","Dessert"), 
        ("beverage","Beverage"), ("side_dish","Side Dish")
    )

    DIETARY_INFO = (
        ("vegetarian","Vegetarian"), ("vegan","Vegan"), ("gluten_free","Gluten-Free"), 
        ("dairy_free","Dairy-Free"), ("none","None")
    )

    restaurant = models.ForeignKey(User,on_delete=models.CASCADE,db_index=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10 ,decimal_places=2)
    category = models.CharField(choices=CATEGORY_CHOICES)
    dietary_info = models.CharField(choices=DIETARY_INFO)
    image = models.ImageField()
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField()

    def __str__(self):
       return "{}".format(self.name)

class Order(TimestampedModel):

    STATUS_CHOICES=(
        ("pending","Pending"), ("confirmed","Confirmed"), ("preparing","Preparing"), ("ready","Ready"), 
        ("picked_up","Picked Up"), ("delivered","Delivered"), ("cancelled","Cancelled")
    )

    customer =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders",db_index=True)
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name="orders",db_index=True)
    driver = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    order_number =models.UUIDField(default=uuid.uuid4)
    status = models.CharField(choices=STATUS_CHOICES,db_index=True)
    delivery_address = models.TextField()
    subtotal = models.DecimalField(max_digits=10 ,decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10 ,decimal_places=2)
    tax = models.DecimalField(max_digits=10 ,decimal_places=2)
    total_amount = models.DecimalField(max_digits=10 ,decimal_places=2)
    special_instructions = models.TextField(null=True)
    estimated_delivery_time = models.DateTimeField(null=True)
    actual_delivery_time = models.DateTimeField(null=True)

    def __str__(self):
       return "{}".format(self.order_number)
    
    def calculate_total(self):
        return self.subtotal+self.delivery_fee+self.tax
    
    def can_cancel(self):
        if self.status != 'cancelled' or self.status != 'picked_up' or self.status != 'delivered':
            return False
        return True
    
    def is_delivered(self):
        if self.status == 'delivered':
            return True
        return False
    
class OrderItem(models.Model):
    order = models.ManyToManyField(Order)
    menu_item = models.ManyToManyField(MenuItem)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10 ,decimal_places=2)
    special_instructions = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    def __str__(self):
       return "{}".format(self.menu_item)

class Review(TimestampedModel):
    customer = models.ForeignKey(User,on_delete=models.CASCADE,db_index=True)
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,null=True,db_index=True)
    menu_item = models.ForeignKey(MenuItem,on_delete=models.CASCADE,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(null=True)

    def __str__(self):
       return "{}".format(self.customer)