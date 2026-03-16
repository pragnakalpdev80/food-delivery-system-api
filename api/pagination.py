from rest_framework.pagination import PageNumberPagination,CursorPagination,LimitOffsetPagination

class RestaurantPageNumberPagination(PageNumberPagination):
    page_size = 20

class MenuItemPageNumberPagination(PageNumberPagination):
    page_size = 30

class ReviewLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 50

class OrderCursorPagination(CursorPagination):
    page_size = 25
    ordering = 'created_at'
    cursor_query_param = 'cursor'


