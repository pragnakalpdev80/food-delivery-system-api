from rest_framework import serializers

def validate_image_format(value):
    """ 
    This function validates image format
    It will allow only .jpg, .jpeg and .png files.
    """
    allowed_formats = ['jpg', 'jpeg', 'png']
    values = value.name.split(".")
    if values[-1] not in allowed_formats:
        raise serializers.ValidationError("Only .jpg, .jpeg and .png formats are allowed")
    return value

def validate_image_size_5mb(value):
    """
    This function will validate size of the image size till 5 MB.
    """
    MAX_5MB_FILE_SIZE = 5*1024*1024
    if value.size > MAX_5MB_FILE_SIZE:
        raise serializers.ValidationError("Image Upload Limit : 5 MB")
    return value

def validate_image_size_10mb(value):
    """
    This function will validate size of the image size till 10 MB.
    """
    MAX_10MB_FILE_SIZE = 10*1024*1024
    if value.size > MAX_10MB_FILE_SIZE:
        raise serializers.ValidationError("Image Upload Limit : 10 MB")
    return value

def validate_amount(value):
    """
    This function will validate positive number.
    """
    if value < 0:
        raise serializers.ValidationError("Amount cannot be negetive")
    return value 
