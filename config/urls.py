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
    OfferDetailView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/registration/', RegistrationView.as_view(), name='api-registration'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/profiles/business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('api/profiles/customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
    path('api/profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('api/offers/', OfferListView.as_view(), name='offer-list'),
    path('api/offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]



    
