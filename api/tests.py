from django.test import TestCase
import pytest
from api.models import (
    User, CustomerProfile, DriverProfile, 
    Restaurant, Address, MenuItem, Cart, 
    CartItem, Order, OrderItem, Review
)
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.filter(username='pytest_r', password='Hill@1234').first()

@pytest.fixture
def restaurant(user):
    return Restaurant.objects.filter(owner=user).first()

@pytest.fixture
def restaurant_owner_user(create_user):
    return create_user("owner1", "restaurant_owner", "9000000002")

@pytest.fixture
def restaurant_owner_user(db):
    user = User.objects.create_user(
        email='testro@gmail.com',
        password='testpass123',
        username='testro',
        first_name='Test',
        last_name='Owner',
        phone_no='9809948591',
        user_type='restaurant_owner'
    )
    return user

@pytest.fixture(scope='class')
def owner_restaurant(api_client, restaurant_owner_user):
    api_client.force_authenticate(user=restaurant_owner_user)
    return api_client

@pytest.fixture(scope='class')
def restaurant(db,restaurant_owner_user):
    restaurant = Restaurant.objects.create(
        owner=user,
        name='Test Restaurant',
        description='testing food',
        cuisine_type='indian',
        address='916, Pragnakalp',
        phone_no='9874587496',
        email='resturant@pragnakalp.com',
        opening_time='09:00:00',
        closing_time='23:00:00',
        is_open=True,
        delivery_fee=30.00,
        minimum_order=100,
    )
    assert restaurant

@pytest.mark.django_db
def test_customer():
    user = User.objects.create_user(
        email='testcustomer@gmail.com',
        password='testpass123',
        username='testcustomer',
        first_name='Test',
        last_name='Customer',
        phone_no='9856748591',
        user_type='customer'
    )
    assert user

@pytest.mark.django_db
def test_delivery_driver():
    user = User.objects.create_user(
        email='testdriver@gmail.com',
        password='testpass123',
        username='testdriver',
        first_name='Test',
        last_name='Driver',
        phone_no='9856948591',
        user_type='delivery_driver'
    )
    assert user

@pytest.mark.django_db
def test_restaurant_owner():
    user = User.objects.create_user(
        email='testro@gmail.com',
        password='testpass123',
        username='testro',
        first_name='Test',
        last_name='Owner',
        phone_no='9809948591',
        user_type='restaurant_owner'
    )
    assert user

@pytest.mark.django_db
class CustomerAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.client = APIClient()  
        self.user = User.objects.create_user(
            email='testcustomer@gmail.com',
            password='testpass123',
            username='testcustomer',
            first_name='Test',
            last_name='Customer',
            phone_no='9856748591',
            user_type='customer'
        )
        token = AccessToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_users(self):
        """Test retrieving customer list"""
        response = self.client.get('/api/v1/customers/',HTTP_AUTHORIZATION=f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc1NTYxMDQ5LCJpYXQiOjE3NzU1NTc0NDksImp0aSI6IjkxODM3MzY0ODBhNTQwODE5ZTlmYjE2MDU4ODFiM2FjIiwidXNlcl9pZCI6IjMifQ.rB3IdidVf2jiXfk-TV0jJZ8dmNrjZ2NBLgJ8k19zT5g")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user(self):
        """Test retrieving single user"""
        response = self.client.get(f'/api/v1/customers/{self.user.customer_profile.id}/')  # GET specific article 
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Verify success
        self.assertEqual(response.data['id'], self.user.customer_profile.id)  # Check correct article returned

    def test_retrieve_another_user(self):
        """Test retrieving single user using another user's JWT"""
        response = self.client.get(f'/api/v1/customers/1/')  
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Verify success

@pytest.mark.django_db
class DriverAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.client = APIClient()  
        self.user = User.objects.create_user(
            email='test1customer@gmail.com',
            password='testpass123',
            username='test1customer',
            first_name='Test',
            last_name='Driver',
            phone_no='9856748591',
            user_type='delivery_driver'
        )
        token = AccessToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_driver(self):
        """Test retrieving customer list"""
        response = self.client.get('/api/v1/drivers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_driver(self):
        """Test retrieving single user"""
        response = self.client.get(f'/api/v1/drivers/{self.user.driver_profile.id}/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.assertEqual(response.data['id'], self.user.driver_profile.id) 

    def test_delete_driver(self):
        """Test retrieving single user"""
        response = self.client.delete(f'/api/v1/drivers/{self.user.driver_profile.id}/') 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(f'/api/v1/drivers/{self.user.driver_profile.id}/') 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_another_user(self):
        """Test retrieving single user using another user's JWT"""
        response = self.client.get(f'/api/v1/drivers/1/')  
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_driver(self):
        update_data={'vehicle_type':'car'}
        response = self.client.patch(f'/api/v1/drivers/{self.user.driver_profile.id}/',update_data)  # GET specific article 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(response.data['vehicle_type'], self.user.driver_profile.vehicle_type)  # Check correct article returned

    def test_rate_limit_exceeded(self):
        """Test requests exceeding rate limit are throttled"""
        for i in range(1001):
            response = self.client.get('/api/v1/drivers/')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

@pytest.mark.django_db
class RestaurantAPITestcase(APITestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.client = APIClient()  
        self.user = User.objects.create_user(
            email='test1customer@gmail.com',
            password='testpass123',
            username='test1customer',
            first_name='Test',
            last_name='Driver',
            phone_no='9856748591',
            user_type='restaurant_owner'
        )
        self.valid_data = {  
            "name": "Smooth operator",
            "description": "idk",
            "cuisine_type": "italian",
            "address": "pata nahi",
            "phone_no": 9874859614,
            "email": "user@example.com",
            "opening_time": "13:02:30",
            "closing_time": "13:02:30",
            "is_open": True,
            "delivery_fee": "10",
            "minimum_order": "100"
        }
        self.restaurant = Restaurant.objects.create(
            owner= self.user,
            name='Test Restaurant',
            description='testing food',
            cuisine_type='indian',
            address='916, Pragnakalp',
            phone_no='9874587496',
            email='resturant@pragnakalp.com',
            opening_time='09:00:00',
            closing_time='23:00:00',
            is_open=True,
            delivery_fee=30.00,
            minimum_order=100,
        )
        token = AccessToken.for_user(user=self.user)
        self.client.force_authenticate(self.user,token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_restaurants(self):
        """Test retrieving customer list"""
        response = self.client.get('/api/v1/restaurants/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_restaurant(self):
        """Test retrieving single restaurant"""
        response = self.client.get(f'/api/v1/restaurants/{self.restaurant.id}/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.assertEqual(response.data['id'], self.user.restaurant_owner.id) 

    def test_retrieve_restaurant_menu(self):
        """Test retrieving single restaurant"""
        response = self.client.get(f'/api/v1/restaurants/{self.restaurant.id}/menu/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
   
    def test_update_restaurant_success(self):

        update_data = {'name': 'Updated Title'}
        response = self.client.patch(f'/api/v1/restaurants/{self.restaurant.id}/',update_data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.name, 'Updated Title')

@pytest.mark.django_db
class MenuAPITestcase(APITestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.client = APIClient()  
        self.customer_client = APIClient()
        self.user = User.objects.create_user(
            email='testowner@gmail.com',
            password='testpass123',
            username='test1restaurant',
            first_name='Test',
            last_name='rest',
            phone_no='9856748591',
            user_type='restaurant_owner'
        )
        self.customer = User.objects.create_user(
            email='testcustomer@gmail.com',
            password='testpass123',
            username='test1customer',
            first_name='Test',
            last_name='cust',
            phone_no='9856741591',
            user_type='customer'
        )
        self.valid_data = {
            "name": "string",
            "description": "string",
            "price": 1000,
            "category": "appetizer",
            "dietary_info": "vegetarian",
            "is_available": True,
            "preparation_time": 10
        }
        self.restaurant = Restaurant.objects.create(
            owner= self.user,
            name='Test Restaurant',
            description='testing food',
            cuisine_type='indian',
            address='916, Pragnakalp',
            phone_no='9874587496',
            email='resturant@pragnakalp.com',
            opening_time='09:00:00',
            closing_time='23:00:00',
            is_open=True,
            delivery_fee=30.00,
            minimum_order=100,
        )
        self.item = MenuItem.objects.create(
            restaurant = self.restaurant ,
            name = "string",
            description = "string",
            price = 1000,
            category = "appetizer",
            dietary_info = "vegetarian",
            is_available = True,
            preparation_time = 10
        )
        token = AccessToken.for_user(user=self.user)
        self.client.force_authenticate(self.user,token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        customer_token = AccessToken.for_user(user=self.customer)
        self.customer_client.force_authenticate(self.customer,customer_token)
        self.customer_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')


    def test_list_menu(self):
        """Test retrieving customer list"""
        response = self.client.get('/api/v1/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_restaurant_menu_item(self):
        """Test retrieving single restaurant"""
        response = self.client.get(f'/api/v1/menu-items/{self.item.id}/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_menu(self):
        """Test creating single iyem"""
        response = self.client.post(f'/api/v1/menu-items/',self.valid_data)  
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  

    def test_update_menu_success(self):
        update_data = {'name': 'Updated Title'}
        response = self.client.patch(f'/api/v1/menu-items/{self.item.id}/',update_data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Title')

    def test_update_menu_fail(self):
        update_data = {'name': 'Updated Title'}
        response = self.customer_client.patch(f'/api/v1/menu-items/{self.restaurant.id}/',update_data)  
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  


@pytest.mark.django_db
class CartAPITestcase(APITestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.rest_client = APIClient()  
        self.customer_client = APIClient()
        self.driver_client = APIClient()
        self.restaurant_owner = User.objects.create_user(
            email='testowner@gmail.com',
            password='testpass123',
            username='test1restaurant',
            first_name='Test',
            last_name='rest',
            phone_no='9856748591',
            user_type='restaurant_owner'
        )
        self.customer = User.objects.create_user(
            email='test2customer@gmail.com',
            password='testpass123',
            username='test1customer2',
            first_name='Test',
            last_name='cust',
            phone_no='9956741591',
            user_type='customer'
        )
      
        self.driver = User.objects.create_user(
            email='testdriver@gmail.com',
            password='testpass123',
            username='test1driver',
            first_name='Test',
            last_name='driver',
            phone_no='9816741591',
            user_type='delivery_driver'
        )
        
        self.restaurant = Restaurant.objects.create(
            owner= self.restaurant_owner,
            name='Test Restaurant',
            description='testing food',
            cuisine_type='indian',
            address='916, Pragnakalp',
            phone_no='9874587496',
            email='resturant@pragnakalp.com',
            opening_time='09:00:00',
            closing_time='23:00:00',
            is_open=True,
            delivery_fee=30.00,
            minimum_order=100,
        )
        self.item = MenuItem.objects.create(
            restaurant = self.restaurant ,
            name = "string",
            description = "string",
            price = 1000,
            category = "appetizer",
            dietary_info = "vegetarian",
            is_available = True,
            preparation_time = 10
        )
        self.valid_data = {
            "menu_item": self.item.id,
            "quantity": 10,
            "special_instructions": "nothing"
        }
        restaurant_owner_token = AccessToken.for_user(user=self.restaurant_owner)
        self.rest_client.force_authenticate(self.restaurant_owner,restaurant_owner_token)
        self.rest_client.credentials(HTTP_AUTHORIZATION=f'Bearer {restaurant_owner_token}')
        customer_token = AccessToken.for_user(user=self.customer)
        self.customer_client.force_authenticate(self.customer,customer_token)
        self.customer_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        driver_token = AccessToken.for_user(user=self.driver)
        self.driver_client.force_authenticate(self.driver,driver_token)
        self.driver_client.credentials(HTTP_AUTHORIZATION=f'Bearer {driver_token}')

    def test_retrieve_cart_success(self):
        """Test retrieving single cart"""
        response = self.customer_client.get(f'/api/v1/cart/{self.customer.customer_profile.cart.id}/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_cart_fail(self):
        """Test retrieving single cart"""
        response = self.driver_client.get(f'/api/v1/cart/{self.customer.customer_profile.cart.id}/')  
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_item_cart_success(self):
        """Test retrieving single cart"""
        response = self.customer_client.post(f'/api/v1/cart-items/',self.valid_data) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

@pytest.mark.django_db
class OrderAPITestcase(APITestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.rest_client = APIClient()  
        self.customer_client = APIClient()
        self.driver_client = APIClient()
        self.restaurant_owner = User.objects.create_user(
            email='testowner@gmail.com',
            password='testpass123',
            username='test1restaurant',
            first_name='Test',
            last_name='rest',
            phone_no='9856748591',
            user_type='restaurant_owner'
        )
        self.customer = User.objects.create_user(
            email='test2customer@gmail.com',
            password='testpass123',
            username='test1customer2',
            first_name='Test',
            last_name='cust',
            phone_no='9956741591',
            user_type='customer'
        )
        self.address = Address.objects.create(
            user = self.customer,
            address_name = "string",
            address = "string",
            is_default = True
        )
        self.driver = User.objects.create_user(
            email='testdriver@gmail.com',
            password='testpass123',
            username='test1driver',
            first_name='Test',
            last_name='driver',
            phone_no='9816741591',
            user_type='delivery_driver'
        )
        
        self.restaurant = Restaurant.objects.create(
            owner= self.restaurant_owner,
            name='Test Restaurant',
            description='testing food',
            cuisine_type='indian',
            address='916, Pragnakalp',
            phone_no='9874587496',
            email='resturant@pragnakalp.com',
            opening_time='09:00:00',
            closing_time='23:00:00',
            is_open=True,
            delivery_fee=30.00,
            minimum_order=100,
        )
        self.item = MenuItem.objects.create(
            restaurant = self.restaurant ,
            name = "string",
            description = "string",
            price = 1000,
            category = "appetizer",
            dietary_info = "vegetarian",
            is_available = True,
            preparation_time = 10
        )
        self.order = Order.objects.create(
            customer= self.customer.customer_profile,
            restaurant= self.restaurant,
            driver= self.driver.driver_profile,
            status='pending',
            delivery_address = self.address,
            subtotal = 54.5,
            delivery_fee = 996,
            tax = 137328,
            total_amount= 87840,
        )

        self.order2 = Order.objects.create(
            customer= self.customer.customer_profile,
            restaurant= self.restaurant,
            driver= self.driver.driver_profile,
            status='ready',
            delivery_address = self.address,
            subtotal = 54.5,
            delivery_fee = 996,
            tax = 137328,
            total_amount= 87840,
        )

        self.valid_data = {
            "status":"confirmed"
        }

        self.invalid_data = {
            "status":"ready"
        }

        self.driver_valid_data = {
            "status":"picked_up"
        }

        self.driver_invalid_data = {
            "status":"confirmed"
        }

        restaurant_owner_token = AccessToken.for_user(user=self.restaurant_owner)
        self.rest_client.force_authenticate(self.restaurant_owner,restaurant_owner_token)
        self.rest_client.credentials(HTTP_AUTHORIZATION=f'Bearer {restaurant_owner_token}')
        customer_token = AccessToken.for_user(user=self.customer)
        self.customer_client.force_authenticate(self.customer,customer_token)
        self.customer_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        driver_token = AccessToken.for_user(user=self.driver)
        self.driver_client.force_authenticate(self.driver,driver_token)
        self.driver_client.credentials(HTTP_AUTHORIZATION=f'Bearer {driver_token}')

    def test_retrieve_order_success(self):
        response = self.customer_client.get(f'/api/v1/orders/{self.order.id}/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_restaurant_success(self):
        response = self.rest_client.post(f'/api/v1/orders/{self.order.id}/update-status/', self.valid_data) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_restaurant_fail(self):
        response = self.rest_client.post(f'/api/v1/orders/{self.order.id}/update-status/', self.invalid_data) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_driver_success(self):
        response = self.driver_client.post(f'/api/v1/orders/{self.order2.id}/update-status/', self.driver_valid_data) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_driver_fail(self):
        response = self.driver_client.post(f'/api/v1/orders/{self.order2.id}/update-status/', self.driver_invalid_data) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
