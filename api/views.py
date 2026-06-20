from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Profile, Offer, OfferDetail, Order
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    ProfileSerializer,
    CustomerListSerializer,
    OfferSerializer, OfferCreateSerializer, SingleOfferSerializer, OfferPatchSerializer, OfferDetailSerializer, OrderSerializer
)
from .pagination import OfferPagination
from .permissions import IsOwnerProfile, IsBusinessProfile, IsOwnerOrReadOnly, IsCustomer, IsOrderParticipant
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from django.db.models import Q


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


class OfferListView(generics.ListCreateAPIView):
    pagination_class = OfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessProfile()]
        return [AllowAny()]

    def get_queryset(self):
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
        try:
            return super().list(request, *args, **kwargs)
        except ValueError:
            return Response(
                {"detail": "Ungültige Anfrageparameter."},
                status=status.HTTP_400_BAD_REQUEST
            )


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    lookup_field = 'pk'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return OfferPatchSerializer
        return SingleOfferSerializer


class SingleOfferDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Für GET (Liste anzeigen) reicht es, eingeloggt zu sein.
        Für POST (Bestellung erstellen) MUSS man zusätzlich 'customer' sein.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomer()]
        return [IsAuthenticated()]

    def get_queryset(self):

        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):

        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response(
                {"detail": "Ungültige Anfragedaten ('offer_detail_id' fehlt oder ungültig ist)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response(
                {"detail": "Das angegebene Angebotsdetail wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        business_user = offer_detail.offer.user

        order = Order.objects.create(
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

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]

        return [IsAuthenticated(), IsOrderParticipant()]

    def update(self, request, *args, **kwargs):

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

        return super().update(request, *args, **kwargs)
