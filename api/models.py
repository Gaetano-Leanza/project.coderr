"""
Database models for the API application.

This module defines the core data structures (tables) for the application, 
including user profiles, business offers, pricing tiers, orders, and reviews. 
It heavily utilizes Django's ORM (Object-Relational Mapping) to manage 
database relationships and constraints.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    """
    Extends the default Django User model with additional profile information.
    
    This model is linked one-to-one with the built-in User model and distinguishes 
    between different account types (e.g., 'customer' or 'business').
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    file = models.FileField(
        upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, default="")
    tel = models.CharField(max_length=30, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
    type = models.CharField(max_length=20, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns a string representation of the profile."""
        return f"Profil von {self.user.username}"


class Offer(models.Model):
    """
    Represents a primary service or product offered by a business user.
    
    This model acts as the parent container for specific pricing tiers 
    (`OfferDetail`). It automatically calculates and stores the minimum 
    price and delivery time based on its associated details for faster querying.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()

    min_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    min_delivery_time = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns the title of the offer."""
        return self.title


class OfferDetail(models.Model):
    """
    Represents a specific pricing and feature tier for an Offer.
    
    Each `Offer` typically has three of these associated with it 
    (e.g., 'basic', 'standard', 'premium'), each defining its own 
    price, delivery time, and feature set.
    """
    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_in_days = models.IntegerField()
    description = models.TextField(blank=True, default="")
    revisions = models.IntegerField(default=0)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, default='basic')

    def __str__(self):
        """Returns a string identifying which offer this detail belongs to."""
        return f"Detail für {self.offer.title}"


class Order(models.Model):
    """
    Represents a transaction between a customer and a business user.
    
    When a customer purchases a specific `OfferDetail`, this model takes 
    a "snapshot" of the detail's properties (price, features, etc.) at 
    the time of purchase to ensure historical accuracy, even if the original 
    offer is later modified.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Bearbeitung'),
        ('completed', 'Abgeschlossen'),
        ('cancelled', 'Storniert'),
    ]

    customer_user = models.ForeignKey(
        User, related_name='customer_orders', on_delete=models.CASCADE)
    business_user = models.ForeignKey(
        User, related_name='business_orders', on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns the order ID and its title."""
        return f"Order #{self.id} - {self.title}"


class Review(models.Model):
    """
    Represents a rating and feedback left by a customer for a business user.
    
    Includes database-level validation to ensure the rating remains 
    strictly between 1 and 5.
    """
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='business_reviews')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns a string identifying the reviewer and the reviewed business."""
        return f"Review by {self.reviewer.username} for {self.business_user.username}"