from rest_framework.throttling import UserRateThrottle

class OrderCreateThrottle(UserRateThrottle):
    scope = 'order_create'
    rate = '20/hour'

class ReviewCreateThrottle(UserRateThrottle):
    scope = 'review_create'
    rate = '10/hour'

class LocationUpdateThrottle(UserRateThrottle):
    scope = 'location_update'
    rate = '500/hour'