from django.urls import path
from . import views

app_name = "expense"

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
]