from django.test import TestCase
import pytest
from api.models import *
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.filter(username='pytest_r', password='Hill@1234').first()

@pytest.fixture
def restaurant(user):
    return Restaurant.objects.filter(owner=user).first()

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
    print(f"Customer {user} Created.")
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
    print(f"Driver {user} Created.")
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
    print(f"Restaurant Owner {user} Created.")
    assert user

@pytest.mark.django_db
def test_restaurant(db,user):
    restaurant = Restaurant.objects.create(
        owner_id=user,
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
    print(f"Restaurant {restaurant} Created.")
    assert restaurant

@pytest.mark.django_db
def test_menu_items(db,restaurant):
    item = MenuItem.objects.create(
        restaurant=restaurant,
        name='Cheeze Paneer',
        description='paneer with delicious cheeze',
        price=250.00,
        category='main_course',
        dietary_info='vegetarian',
        is_available=True,
        preparation_time=5,
    )
    print(f"Menu Item {item} Created.")
    assert item
