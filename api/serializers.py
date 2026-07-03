"""
Serializers for the API application.

This module converts complex data types, such as Django model instances, into 
native Python datatypes that can then be easily rendered into JSON. It also 
provides deserialization, validating incoming parsed data before saving it 
to the database.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Offer, OfferDetail, Order, Review


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling new user registrations.

    Validates the user's email and password, creates the core User object, 
    and automatically generates the corresponding Profile.
    """
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, data):
        """
        Validates the provided registration data.

        Checks that the passwords match and that the email address is 
        not already registered in the system.

        Args:
            data (dict): The unvalidated dictionary of input data.

        Raises:
            serializers.ValidationError: If passwords mismatch or email exists.

        Returns:
            dict: The validated data.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Passwörter stimmen nicht überein."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"email": "Ein Benutzer mit dieser E-Mail existiert bereits."})
        return data

    def create(self, validated_data):
        """
        Creates a new User and their linked Profile.

        Args:
            validated_data (dict): The cleaned and validated incoming data.

        Returns:
            User: The newly created User instance.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        Profile.objects.create(
            user=user,
            type=user_type
        )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.

    Simply accepts and validates the presence of a username and password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating user profiles.

    Includes read-only fields pulled directly from the associated User model.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    email = serializers.CharField(source='user.email')

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours',
            'type', 'email', 'created_at'
        ]

    def update(self, instance, validated_data):
        """
        Updates the profile instance and handles nested user data safely.

        Specifically extracts the email from the nested user dictionary to update 
        the associated User model directly, avoiding DRF's default nested update errors.
        """

        user_data = validated_data.pop('user', {})
        new_email = user_data.get('email')

        if new_email:
            instance.user.email = new_email
            instance.user.save()

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Customizes the serialized output.

        Translates `None` values strictly to empty strings ("") to prevent 
        rendering issues or crashes in frontend frameworks.
        """
        data = super().to_representation(instance)
        for key, value in data.items():
            if value is None:
                data[key] = ""
        return data


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for listing customer profiles.

    Provides a condensed view of the profile data suitable for list displays.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    uploaded_at = serializers.DateTimeField(
        source='created_at', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type'
        ]

    def to_representation(self, instance):
        """
        Customizes the serialized output.

        Ensures that specific string fields return empty strings ("") 
        instead of `None`.
        """
        data = super().to_representation(instance)
        string_fields = ['first_name', 'last_name', 'file']
        for field in string_fields:
            if data.get(field) is None:
                data[field] = ""
        return data


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Offers.

    Includes dynamically constructed custom fields for user details 
    and nested offer details.
    """
    user_details = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        """
        Constructs a dictionary containing the offer creator's basic info.
        """
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

    def get_details(self, obj):
        """
        Retrieves related OfferDetails using the 'details' related_name.
        Returns a list of dictionaries with IDs and relative URLs.
        """
        return [
            {
                "id": detail.id,
                "url": f"/offerdetails/{detail.id}/"
            }
            for detail in obj.details.all()
        ]


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the sub-components (pricing tiers) of an Offer.
    """
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Offer alongside its nested OfferDetails.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        """
        Validates the incoming nested details array.

        Ensures that exactly three pricing tiers are provided and that they 
        strictly match the required types: 'basic', 'standard', and 'premium'.
        """
        if len(value) != 3:
            raise serializers.ValidationError(
                "Ein Offer muss genau 3 Details enthalten!")

        types = [d.get('offer_type') for d in value]
        if sorted(types) != ['basic', 'premium', 'standard']:
            raise serializers.ValidationError(
                "Die Details müssen 'basic', 'standard' und 'premium' enthalten.")
        return value

    def create(self, validated_data):
        """
        Overrides the default create method to handle nested object creation.

        Calculates the minimum price and minimum delivery time from the provided 
        details, creates the parent Offer, and then creates the three child 
        OfferDetail records.
        """
        details_data = validated_data.pop('details')
        user = self.context['request'].user

        min_price = min([d['price'] for d in details_data])
        min_delivery_time = min([d['delivery_time_in_days']
                                for d in details_data])

        offer = Offer.objects.create(
            user=user,
            min_price=min_price,
            min_delivery_time=min_delivery_time,
            **validated_data
        )

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer


class SingleOfferSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a single, highly detailed Offer view.
    """
    details = serializers.SerializerMethodField()
    min_price = serializers.FloatField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time'
        ]

    def get_details(self, obj):
        """
        Retrieves related OfferDetails and constructs absolute URIs 
        for their endpoints based on the current request context.
        """
        request = self.context.get('request')

        return [
            {
                "id": detail.id,
                "url": request.build_absolute_uri(f"/api/offerdetails/{detail.id}/") if request else f"http://127.0.0.1:8000/api/offerdetails/{detail.id}/"
            }
            for detail in obj.details.all()
        ]


class OfferPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for handling partial updates (PATCH) to an Offer and its details.
    """
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Validates that at least one field is provided for the PATCH request.
        """
        if not data and not self.initial_data:
            raise serializers.ValidationError(
                {"detail": "Keine Daten für das Update bereitgestellt."}
            )

        if 'details' in data:
            details_data = data['details']

        if not details_data:
            raise serializers.ValidationError(
                {"details": "Details dürfen nicht leer sein, wenn sie bereitgestellt werden."}
            )

        for detail_item in details_data:
            if not detail_item.get('offer_type'):
                raise serializers.ValidationError(
                    {"details": "Der 'offer_type' (basic, standard, premium) muss mitgegeben werden, um ein Detail zu aktualisieren."}
                )

        return data

    def update(self, instance, validated_data):
        """
        Overrides the default update method to manage nested details safely.
        """
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for detail_item in details_data:
                offer_type = detail_item.get('offer_type')

                if offer_type:
                    OfferDetail.objects.update_or_create(
                        offer=instance,
                        offer_type=offer_type,
                        defaults=detail_item
                    )

            current_details = instance.details.all()
            if current_details.exists():
                instance.min_price = min([d.price for d in current_details])
                instance.min_delivery_time = min(
                    [d.delivery_time_in_days for d in current_details])
                instance.save()

        return instance


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for managing customer Orders.
    Includes validation to prevent creation of orders with missing essential data.
    """

    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(),
        write_only=True,
        required=True,
        error_messages={
            'incorrect_type': "Ungültige Anfragedaten: 'offer_detail_id' muss eine Zahl sein.",
            'does_not_exist': "Das angegebene Angebotsdetail wurde nicht gefunden.",
            'null': "Ungültige Anfragedaten: 'offer_detail_id' darf nicht null sein."
        }
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price',
            'features', 'offer_type', 'status',
            'created_at', 'updated_at',
            'offer_detail_id'
        ]

        read_only_fields = ['id', 'customer_user',
                            'business_user', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validates that critical order fields are present and valid.
        """

        if not data.get('title'):
            raise serializers.ValidationError(
                {"title": "Ein Titel für die Bestellung ist erforderlich."})

        if data.get('price', 0) < 0:
            raise serializers.ValidationError(
                {"price": "Der Preis darf nicht negativ sein."})

        return data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user Reviews on business profiles.
    """
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'created_at', 'updated_at']


class BusinessProfileListSerializer(ProfileSerializer):
    """
    Serializer for listing business profiles.
    Inherits from ProfileSerializer but restricts the output fields 
    to match the API documentation (hides email and created_at).
    """
    class Meta(ProfileSerializer.Meta):
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]
