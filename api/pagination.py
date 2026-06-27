"""
Pagination classes for the API application.

This module defines how large sets of data (like querysets of Offers) 
are split into smaller, manageable "pages" before being sent to the client. 
This prevents performance issues and massive payloads when the database grows.
"""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    Custom pagination class for Offer lists.
    
    This class inherits from Django REST Framework's PageNumberPagination 
    and sets specific limits for how many offers are returned per request.
    
    Attributes:
        page_size (int): The default number of items returned per page (10).
        page_size_query_param (str): The URL query parameter that allows the 
            client to request a specific page size (e.g., `?page_size=20`).
        max_page_size (int): The absolute maximum number of items the server 
            will return in a single request (100), regardless of what the 
            client asks for via `page_size_query_param`. This is a security 
            measure to prevent server overload.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100