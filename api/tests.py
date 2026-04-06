from django.test import TestCase

# Create your tests here.
# api/tests.py
import pytest
from api.models import *
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def customer():
    user = User.objects.create_user(
        email='testcustomer@gmail.com',
        password='testpass123',
        username='testcustomer',
        first_name='Test',
        last_name='Customer',
        phone_no='9856748591',
        user_type='customer'
    )
     # print(f"Customer Created")
    return user

@pytest.fixture
def delivery_driver():
    user = User.objects.create_user(
        email='testdriver@gmail.com',
        password='testpass123',
        username='testdriver',
        first_name='Test',
        last_name='Driver',
        phone_no='9856948591',
        user_type='delivery_driver'
    )
     # print(f"Driver Created")
    return user

@pytest.fixture
def restaurant_owner():
    user = User.objects.create_user(
        email='testro@gmail.com',
        password='testpass123',
        username='testro',
        first_name='Test',
        last_name='Owner',
        phone_no='9809948591',
        user_type='restaurant_owner'
    )
     # print(f"Driver Created")
    return user

@pytest.fixture
def restaurant(db,restaurant_owner):
    restaurant = Restaurant.objects.create(
        owner=restaurant_owner,
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
     # print(f"Restaurant {restaurant} Created")
    return restaurant

@pytest.fixture
def menu_items(db,restaurant):
    item1 = MenuItem.objects.create(
        restaurant=restaurant,
        name='Paneer Butter Masala',
        description='paneer',
        price=Decimal('250.00'),
        category='m',
        dietary_info='v1',
        is_available=True,
    )
    item2 = MenuItem.objects.create(
        restaurant=restaurant,
        name='Dal Tadka',
        description='dal with tadka',
        price=Decimal('150.00'),
        category='m',
        dietary_info='v1',
        is_available=True,
    )
    item3 = MenuItem.objects.create(
        restaurant=restaurant,
        name='Gulab Jamun',
        description='dessert',
        price=Decimal('80.00'),
        category='d',
        dietary_info='no',
        is_available=False,
    )
    return [item1,item2,item3]
