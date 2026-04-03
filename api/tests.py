from django.test import TestCase

# Create your tests here.
# api/tests.py
import pytest
from api.models import User
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
        email='testcustomer@test.com',
        password='testpass123',
        username='testcustomer',
        first_name='Test',
        last_name='Customer',
        phone_number='9856748591',
        user_type='customer'
    )
    print(f"Customer Created")
    return user