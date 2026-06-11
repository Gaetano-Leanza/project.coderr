from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters  
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Profile, Offer 
from .serializers import (
    RegistrationSerializer, 
    LoginSerializer, 
    ProfileSerializer, 
    CustomerListSerializer, 
    OfferSerializer
)
from .pagination import OfferPagination
from .permissions import IsOwnerProfile


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id
                }, status=status.HTTP_200_OK)

            return Response({"error": "Ungültige Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerProfile]


class BusinessProfileListView(generics.ListAPIView):
    queryset = Profile.objects.filter(type='business')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    queryset = Profile.objects.filter(type='customer')
    serializer_class = CustomerListSerializer
    permission_classes = [IsAuthenticated]


class OfferListView(generics.ListAPIView):
    """
    Gibt eine paginierte Liste von Angeboten zurück. 
    Unterstützt Suche (?search=) und Filterung (min_price, max_delivery_time, creator_id).
    """
    serializer_class = OfferSerializer
    pagination_class = OfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_queryset(self):
        
        queryset = Offer.objects.all()
        
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')

        if creator_id is not None:
            queryset = queryset.filter(user_id=creator_id)
            
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)
            
        if max_delivery_time is not None:
            queryset = queryset.filter(min_delivery_time__lte=max_delivery_time)

        return queryset