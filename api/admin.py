"""
Django Admin configuration for the API application.

This module registers the application's models with the Django Admin site, 
allowing administrators to manage, view, and edit database records directly 
through the browser interface.
"""

from django.contrib import admin
from .models import Profile, Offer, OfferDetail, Order, Review

# ==========================================
# Admin Model Registration
# ==========================================
# By default, we register the models directly.
# PRO TIP: To improve the admin UI, you can define a class inheriting 
# from admin.ModelAdmin and register it like: 
# @admin.register(ModelName)
# class ModelNameAdmin(admin.ModelAdmin):
#     list_display = (...)
#     search_fields = (...)

admin.site.register(Profile)
admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Order)
admin.site.register(Review)