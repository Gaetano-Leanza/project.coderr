"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import (
    BusinessProfileListView,
    CustomerProfileListView,
    RegistrationView,
    LoginView,
    ProfileDetailView,
    OfferListView,
    OfferDetailView, SingleOfferDetailView, OrderListCreateView, OrderDetailView, OrderCountView, CompletedOrderCountView, ReviewListCreateView, ReviewDetailView, BaseInfoView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/registration/', RegistrationView.as_view(), name='api-registration'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/profiles/business/', BusinessProfileListView.as_view(),
         name='business-profile-list'),
    path('api/profiles/customer/', CustomerProfileListView.as_view(),
         name='customer-profile-list'),
    path('api/profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('api/offers/', OfferListView.as_view(), name='offer-list'),
    path('api/offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('api/offerdetails/<int:pk>/',
         SingleOfferDetailView.as_view(), name='offerdetail-detail'),
    path('api/orders/', OrderListCreateView.as_view(), name='order-list'),
    path('api/orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('api/order-count/<int:business_user_id>/',
         OrderCountView.as_view(), name='order-count'),
    path('api/completed-order-count/<int:business_user_id>/',
         CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('api/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('api/reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('api/base-info/', BaseInfoView.as_view(), name='base-info'),
]
