from django.contrib import admin
from .models import Profile, Offer, OfferDetail, Order


admin.site.register(Profile)
admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Order)