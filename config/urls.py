"""
Main URL configuration for the Django project.

This module acts as the central routing hub for the application. It maps 
incoming HTTP requests to their corresponding class-based views (CBVs) 
within the `api` app.

Attributes:
    urlpatterns (list): A list of url() or path() instances that determine 
        which view handles a given URL string.
"""

from django.contrib import admin
from django.urls import path

# Importing all necessary class-based views from the API application.
from api.views import (
    BusinessProfileListView,
    CustomerProfileListView,
    RegistrationView,
    LoginView,
    ProfileDetailView,
    OfferListView,
    OfferDetailView, 
    SingleOfferDetailView, 
    OrderListCreateView, 
    OrderDetailView, 
    OrderCountView, 
    CompletedOrderCountView, 
    ReviewListCreateView, 
    ReviewDetailView, 
    BaseInfoView
)


urlpatterns = [
    # ==========================================
    # Django Admin Interface
    # ==========================================
    path('admin/', admin.site.urls),

    # ==========================================
    # Authentication Endpoints
    # ==========================================
    path('api/registration/', RegistrationView.as_view(), name='api-registration'),
    path('api/login/', LoginView.as_view(), name='api-login'),

    # ==========================================
    # Profile Management Endpoints
    # ==========================================
    path('api/profiles/business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('api/profiles/customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
    path('api/profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),

    # ==========================================
    # Offer & Offer-Detail Endpoints
    # ==========================================
    path('api/offers/', OfferListView.as_view(), name='offer-list'),
    path('api/offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('api/offerdetails/<int:pk>/', SingleOfferDetailView.as_view(), name='offerdetail-detail'),

    # ==========================================
    # Order Management & Statistics Endpoints
    # ==========================================
    path('api/orders/', OrderListCreateView.as_view(), name='order-list'),
    path('api/orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('api/order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('api/completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),

    # ==========================================
    # Review System Endpoints
    # ==========================================
    path('api/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('api/reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),

    # ==========================================
    # Public Platform Statistics
    # ==========================================
    path('api/base-info/', BaseInfoView.as_view(), name='base-info'),
]