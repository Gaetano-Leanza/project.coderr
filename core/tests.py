"""
Unit tests for the application.

This module is intended to contain automated test cases for the app's 
models, views, and core logic using Django's built-in testing framework.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile


class ProfileTest(TestCase):
    def setUp(self):

        self.user1 = User.objects.create_user(
            username='paul', email='pauline82@test.com', password='pw')
        self.profile1 = Profile.objects.create(
            user=self.user1, type='customer')

        self.user2 = User.objects.create_user(
            username='marie', email='marie27@test.com', password='pw')
        self.profile2 = Profile.objects.create(
            user=self.user2, type='customer')

    def test_profile_email_update(self):

        self.client.force_login(self.user1)

        response = self.client.patch(
            f'/api/profile/{self.profile1.pk}/', {'email': 'pauline82@test.com'})

        self.assertEqual(response.data['email'], 'pauline82@test.com')
