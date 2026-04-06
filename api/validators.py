from rest_framework import serializers
from .models import DriverProfile

def validate_image_format(value):
    allowed_formats = ['jpg', 'jpeg', 'png']
    values = value.name.split(".")
    if values[-1] not in allowed_formats:
        raise serializers.ValidationError("Only .jpg, .jpeg and .png formats are allowed")
    return value

def validate_image_size_5mb(value):
    MAX_5MB_FILE_SIZE = 5*1024*1024
    if value.size > MAX_5MB_FILE_SIZE:
        raise serializers.ValidationError("Image Upload Limit : 5 MB")
    return value

def validate_image_size_10mb(value):
    MAX_10MB_FILE_SIZE = 10*1024*1024
    if value.size > MAX_10MB_FILE_SIZE:
        raise serializers.ValidationError("Image Upload Limit : 10 MB")
    return value

def validate_amount(value):
    if value < 0:
        raise serializers.ValidationError("Amount cannot be negetive")
    return value 

# def validate_driver(self,value):
#      # print(DriverProfile.objects.filter(id=value,is_available=True).query)
#     if value == DriverProfile.objects.filter(id=value,is_available=True):
#         raise serializers.ValidationError(f"{value} is not proper value for priority")
#     return value