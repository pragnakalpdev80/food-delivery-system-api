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
