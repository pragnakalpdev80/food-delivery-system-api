from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    # def has_object_permission(self, request, view, obj):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True 
    #     return obj.owner == request.user
    pass

class IsRestaurantOwner(permissions.BasePermission):
    pass

class IsCustomer(permissions.BasePermission):
    pass

class IsDriver(permissions.BasePermission):
    pass

class IsOrderCustomer(permissions.BasePermission):
    pass

class IsRestaurantOwnerOrDriver(permissions.BasePermission):
    pass