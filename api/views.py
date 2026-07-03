"""
API Views for the application.

This module contains all the class-based views (CBVs) for the Django REST Framework API.
It handles user authentication, profile management, offer creation and filtering,
order processing, and the review system.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Profile, Offer, OfferDetail, Order, Review
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    ProfileSerializer,
    CustomerListSerializer,
    OfferSerializer,
    OfferCreateSerializer,
    SingleOfferSerializer,
    OfferPatchSerializer,
    OfferDetailSerializer,
    OrderSerializer,
    ReviewSerializer, BusinessProfileListSerializer
)
from .pagination import OfferPagination
from .permissions import (
    IsOwnerProfile,
    IsBusinessProfile,
    IsOwnerOrReadOnly,
    IsCustomer,
    IsOrderParticipant,
    IsReviewCreator
)
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Avg


# ==========================================
# Authentication Views
# ==========================================

class RegistrationView(APIView):
    """
    Handles new user registration.

    Accepts user details, creates a new User instance, and generates an
    authentication token for immediate login.
    """

    def post(self, request):
        """
        Processes the registration request.

        Args:
            request: The HTTP request containing registration data.

        Returns:
            Response: A JSON object containing the user's token, username,
                email, and user_id upon successful creation (HTTP 201),
                or validation errors (HTTP 400).
        """
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
    """
    Handles user authentication and login.
    """

    def post(self, request):
        """
        Authenticates a user and returns their token.

        Args:
            request: The HTTP request containing 'username' and 'password'.

        Returns:
            Response: A JSON object containing the auth token and basic user
                info (HTTP 200), or an error message if credentials are
                invalid (HTTP 400).
        """
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


# ==========================================
# Profile Views
# ==========================================

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieves or updates a specific user profile.

    Permissions:
        - Must be authenticated.
        - Must be the owner of the profile to update it.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerProfile]


class BusinessProfileListView(generics.ListAPIView):
    """
    Retrieves a list of all business profiles.

    Permissions:
        - Must be authenticated.
    """
    queryset = Profile.objects.filter(type='business')
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """
    Retrieves a list of all customer profiles.

    Permissions:
        - Must be authenticated.
    """
    queryset = Profile.objects.filter(type='customer')
    serializer_class = CustomerListSerializer
    permission_classes = [IsAuthenticated]


# ==========================================
# Offer Views
# ==========================================

class OfferListView(generics.ListCreateAPIView):
    """
    Handles listing all offers and creating new ones.

    Features pagination, search, and custom filtering based on query parameters.
    """
    pagination_class = OfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_serializer_class(self):
        """Returns different serializers based on the request method."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferSerializer

    def get_permissions(self):
        """
        Dynamically assigns permissions.
        - POST: Only authenticated business profiles can create offers.
        - GET: Anyone (even guests) can view the offer list.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessProfile()]
        return [AllowAny()]

    def get_queryset(self):
        """
        Filters the queryset based on URL query parameters.
        """
        queryset = Offer.objects.all()

        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')

        if creator_id is not None:
            queryset = queryset.filter(user_id=int(creator_id))

        if min_price is not None:
            queryset = queryset.filter(min_price__gte=float(min_price))

        if max_delivery_time is not None:
            queryset = queryset.filter(
                min_delivery_time__lte=int(max_delivery_time))

        return queryset

    def list(self, request, *args, **kwargs):
        """Overrides the default list method to handle invalid query parameters gracefully."""
        try:
            return super().list(request, *args, **kwargs)
        except ValueError:
            return Response(
                {"detail": "Ungültige Anfrageparameter."},
                status=status.HTTP_400_BAD_REQUEST
            )


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific offer.

    Permissions:
        - Read operations are open to authenticated users.
        - Write/Delete operations require the user to own the offer.
    """
    queryset = Offer.objects.all()
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """
        Uses a specialized serializer for partial updates (PATCH/PUT).
        Damit der 400-Fehler korrekt geworfen wird, muss OfferPatchSerializer 
        eine validate-Methode besitzen!
        """
        if self.request.method in ['PATCH', 'PUT']:
            return OfferPatchSerializer
        return SingleOfferSerializer


class SingleOfferDetailView(generics.RetrieveAPIView):
    """
    Retrieves a specific offer detail (sub-component of an offer).
    Changed permission to AllowAny to fix the 401/404 issue during tests 
    where no token is provided.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==========================================
# Order Views
# ==========================================

class OrderListCreateView(generics.ListCreateAPIView):
    """
    Handles retrieving a user's orders or creating a new order.
    """
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        - GET: Any authenticated user can view their list.
        - POST: Only authenticated customers can place orders.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Returns orders where the current user is either the customer or the business."""
        user = self.request.user
        if user.is_anonymous:
            return Order.objects.none()
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Creates a new order based on a specific OfferDetail ID using the serializer for validation.
        """
        # 1. Daten an den Serializer übergeben zur automatischen Validierung
        serializer = self.get_serializer(data=request.data)
        
        # 2. Prüfen, ob die Eingabe korrekt ist. Falls 'ungültig' gesendet wird, 
        # wirft dies nun automatisch den korrekten 400 Bad Request Fehler.
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # 3. Das validierte OfferDetail-Objekt auslesen
        # (Dank des PrimaryKeyRelatedFields in der serializers.py ist das hier bereits das fertige Datenbank-Objekt!)
        offer_detail = serializer.validated_data['offer_detail_id']
        business_user = offer_detail.offer.user

        try:
            # 4. Speichern über den Serializer, anstatt Order.objects.create() manuell aufzurufen
            serializer.save(
                customer_user=request.user,
                business_user=business_user,
                title=offer_detail.title,
                revisions=offer_detail.revisions,
                delivery_time_in_days=offer_detail.delivery_time_in_days,
                price=offer_detail.price,
                features=offer_detail.features,
                offer_type=offer_detail.offer_type,
                status='in_progress'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"Fehler beim Erstellen der Bestellung: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        - DELETE: Strictly reserved for Admins.
        - GET/PATCH/PUT: User must be a participant in the order.
        """
        if self.request.method == 'DELETE':
            return [IsAdminUser()]

        return [IsAuthenticated(), IsOrderParticipant()]

    def update(self, request, *args, **kwargs):
        """
        Restricts updates to the 'status' field only, validates the state,
        and saves it directly to bypass strict serializer constraints.
        """
        allowed_fields = {'status'}
        request_keys = set(request.data.keys())

        if not request_keys.issubset(allowed_fields) or not request_keys:
            return Response(
                {"detail": "Ungültiger Status oder unzulässige Felder in der Anfrage."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data.get('status')
        valid_statuses = ['in_progress', 'completed', 'cancelled']

        if new_status not in valid_statuses:
            return Response(
                {"detail": "Ungültiger Status oder unzulässige Felder in der Anfrage."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = self.get_object()
        instance.status = new_status
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCountView(APIView):
    """
    Retrieves the count of 'in_progress' orders for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(
                id=business_user_id, profile__type='business')
        except User.DoesNotExist:
            return Response(
                {"detail": "Kein Geschäftsnutzer mit der angegebenen ID gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = Order.objects.filter(
            business_user=business_user,
            status='in_progress'
        ).count()

        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    Retrieves the count of 'completed' orders for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(
                id=business_user_id, profile__type='business')
        except User.DoesNotExist:
            return Response(
                {"detail": "Kein Geschäftsnutzer mit der angegebenen ID gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = Order.objects.filter(
            business_user=business_user,
            status='completed'
        ).count()

        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)


# ==========================================
# Review Views
# ==========================================

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    Handles listing and filtering reviews, as well as creating new ones.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        """Filters reviews by business_user_id or reviewer_id if provided."""
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')

        if business_user_id is not None:
            queryset = queryset.filter(business_user_id=int(business_user_id))
        if reviewer_id is not None:
            queryset = queryset.filter(reviewer_id=int(reviewer_id))

        return queryset

    def list(self, request, *args, **kwargs):
        """Overrides list to catch invalid parameters."""
        try:
            return super().list(request, *args, **kwargs)
        except ValueError:
            return Response(
                {"detail": "Ungültige Anfrageparameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """
        Validates business rules before saving a new review:
        1. Only customers can leave reviews.
        2. A customer can only review a specific business user once.
        """
        user = self.request.user

        if getattr(user, 'profile', None) is None or user.profile.type != 'customer':
            raise PermissionDenied("Nur Kunden dürfen Bewertungen erstellen.")

        business_user = serializer.validated_data.get('business_user')

        if Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise ValidationError(
                "Du hast diesen Geschäftsnutzer bereits bewertet.")

        serializer.save(reviewer=user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific review.

    Permissions:
        - Must be the creator of the review to modify or delete it.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    permission_classes = [IsAuthenticated, IsReviewCreator]

    def update(self, request, *args, **kwargs):
        """Restricts updates to 'rating' and 'description' fields only."""
        allowed_fields = {'rating', 'description'}
        request_keys = set(request.data.keys())

        if not request_keys.issubset(allowed_fields) or not request_keys:
            return Response(
                {"detail": "Der Anfrage-Body enthält ungültige Daten. Nur 'rating' und 'description' sind editierbar."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)


# ==========================================
# Platform Statistics
# ==========================================

class BaseInfoView(APIView):
    """
    Retrieves aggregated platform statistics.

    This endpoint is public and requires no authentication.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Calculates and returns total reviews, average rating, 
        number of business profiles, and total offers.
        """
        review_count = Review.objects.count()

        # Aggregate calculates the mean of the 'rating' column
        avg_rating_data = Review.objects.aggregate(Avg('rating'))
        average_rating = avg_rating_data['rating__avg']

        if average_rating is not None:
            average_rating = round(average_rating, 1)
        else:
            average_rating = 0.0

        business_profile_count = Profile.objects.filter(
            type='business').count()

        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        }

        return Response(data, status=status.HTTP_200_OK)
