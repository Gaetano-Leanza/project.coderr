from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Offer


class RegistrationSerializer(serializers.ModelSerializer):
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
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Passwörter stimmen nicht überein."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"email": "Ein Benutzer mit dieser E-Mail existiert bereits."})
        return data

    def create(self, validated_data):
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
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours',
            'type', 'email', 'created_at'
        ]

    def to_representation(self, instance):
        """Übersetzt None-Werte strikt in leere Strings ("") für das Frontend."""
        data = super().to_representation(instance)
        for key, value in data.items():
            if value is None:
                data[key] = ""
        return data


class CustomerListSerializer(serializers.ModelSerializer):
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
        """Sorgt auch hier dafür, dass None zu einem leeren String wird."""
        data = super().to_representation(instance)
        string_fields = ['first_name', 'last_name', 'file']
        for field in string_fields:
            if data.get(field) is None:
                data[field] = ""
        return data


class OfferSerializer(serializers.ModelSerializer):

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
        """Baut das geforderte user_details Objekt aus dem verknüpften User zusammen."""
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

    def get_details(self, obj):
        """Greift über den related_name 'details' auf alle OfferDetails zu."""
        return [
            {
                "id": detail.id,
                "url": f"/offerdetails/{detail.id}/"
            }

            for detail in obj.details.all()
        ]
