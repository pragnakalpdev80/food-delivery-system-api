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

    def test_update_restaurant_success(self):

        update_data = {'name': 'Updated Title'}
        response = self.client.patch(f'/api/v1/restaurants/{self.restaurant.id}/',update_data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.name, 'Updated Title')


