from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    This permission class will allow owners to do all operations
    and others can see only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True 
        return obj.restaurant.owner == request.user

class IsRestaurantOwner(permissions.BasePermission):
    """
    This permission will allow access only to restaurant owner.
    """
    def has_permission(self, request, view):
        return request.user.user_type == 'restaurant_owner'  
    
class IsCustomer(permissions.BasePermission):
    """
    This permission will allow access only to customers.
    """
    def has_permission(self, request, view):
        return request.user.user_type == 'customer'
          
class IsDriver(permissions.BasePermission):
    """
    This permission will allow access only to delivery drivers.
    """
    def has_permission(self, request, view):
        return request.user.user_type == 'delivery_driver'
    
class IsOrderCustomer(permissions.BasePermission):
    """
    This permisson will allow access only to customer who orderded.
    """
    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user

class IsRestaurantOwnerOrDriver(permissions.BasePermission):
    """
    This permission will allow acces to restaurant owner and drivers only.
    """
    def has_object_permission(self, request, view, obj):
        is_restaurant_owner = (
            request.user.user_type == 'restaurant_owner' and 
            obj.restaurant.owner == request.user
        )
        
        is_assigned_driver = (
            request.user.user_type == 'delivery_driver' and
            obj.driver.user == request.user and obj.driver is not None
        )
        
        return is_restaurant_owner or is_assigned_driver
