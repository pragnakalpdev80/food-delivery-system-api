from rest_framework import serializers

def validate_image_format(value):
    print(value.name)
    allowed_formats = ['jpg', 'jpeg', 'png']
    values = value.name.split(".")
    if values[-1] not in allowed_formats:
        print("True")
        serializers.ValidationError("Only .jpg, .jpeg and .png formats are allowed")
    print("False")
    return value

def validate_image_size_5mb(value):
    MAX_5MB_FILE_SIZE = 5*1024*1024
    if value.size > MAX_5MB_FILE_SIZE:
        # print("no")
        serializers.ValidationError("Image Upload Limit : 5 MB")
    # print("yes")
    return value

def validate_image_size_10mb(value):
    MAX_10MB_FILE_SIZE = 10*1024*1024
    if value.size > MAX_10MB_FILE_SIZE:
        serializers.ValidationError("Image Upload Limit : 5 MB")
    return value
