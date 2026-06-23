from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
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
        return f"Profil von {self.user.username}"


class Offer(models.Model):

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
        return self.title


class OfferDetail(models.Model):
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
        return f"Detail für {self.offer.title}"


class Order(models.Model):
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
        return f"Order #{self.id} - {self.title}"


class Review(models.Model):
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
        return f"Review by {self.reviewer.username} for {self.business_user.username}"
