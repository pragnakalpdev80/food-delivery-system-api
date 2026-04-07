from rest_framework.throttling import UserRateThrottle

class OrderCreateThrottle(UserRateThrottle):
    """
    This throttle will limit the rate of order creation till 20 attempts per hour.
    """
    scope = 'order_create'
    rate = '20/hour'

class ReviewCreateThrottle(UserRateThrottle):
    """
    This throttle will limit the rate of review creation till 10 attempts per hour.
    """
    scope = 'review_create'
    rate = '10/hour'

class LocationUpdateThrottle(UserRateThrottle):
    """
    This throttle will limit the rate of location updates till 500 attempts per hour.
    """
    scope = 'location_update'
    rate = '500/hour'