from rest_framework.pagination import PageNumberPagination,CursorPagination,LimitOffsetPagination

class RestaurantPageNumberPagination(PageNumberPagination):
    """
    Only 20 restaurant will load on 1 page.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MenuItemPageNumberPagination(PageNumberPagination):
    """
    Only 30 menu items will load on 1 page.
    """
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReviewLimitOffsetPagination(LimitOffsetPagination):
    """
    Only default 20 and up to 50 reviews will load on 1 page.
    """
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 50

class OrderCursorPagination(CursorPagination):
    """
    Only 25 orders will load on 1 page.
    """
    page_size = 25
    ordering = 'created_at'
    cursor_query_param = 'cursor'


