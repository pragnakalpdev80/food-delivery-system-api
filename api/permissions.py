from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True 
        return obj.owner == request.user

class IsRestaurantOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'restaurant_owner'
             
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'customer'
          
class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'delivery_driver'
    
class IsOrderCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user

class IsRestaurantOwnerOrDriver(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_restaurant_owner = (
            request.user.user_type == 'restaurant_owner' and 
            obj.restaurant.owner == request.user
        )
        
        is_assigned_driver = (
            request.user.user_type == 'delivery_driver' and
            obj.driver.user == request.user
        )
        
        return is_restaurant_owner or is_assigned_driver

class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True 
        return request.user.user_type == 'restaurant_owner'