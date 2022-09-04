from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_psq import PsqMixin, Rule
from rest_framework.viewsets import GenericViewSet

from ads.models import Announcement
from housing.models import ResidentialComplex
from .permissions import IsMyFilter
from .services.month_ahead import get_range_month
from .models import (
    Notary, Contact, Subscription, Message, Filter
)
from .serializers import (
    NotarySerializer, UserProfileSerializer, UserAgentSerializer, UserSubscriptionSerializer,
    MessageSerializer, FilterSerializer, UserNotificationSerializer, UserPerAgentSerializer,
    UserAutoRenewalSubscriptionSerializer, UserListSerializer, UserFavoritesAnnouncementSerializer,
    UserFavoritesResidentialComplexSerializer
)

User = get_user_model()


# Create your views here.

class FilterViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = FilterSerializer
    permission_classes = [IsAuthenticated, IsMyFilter]

    psq_rules = {
        ('create',): [Rule([IsAuthenticated])]
    }

    def get_queryset(self):
        queryset = Filter.objects.filter(user=self.request.user).select_related('user')
        return queryset


class NotaryViewSet(PsqMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = NotarySerializer
    queryset = Notary.objects.all()
    parser_classes = [MultiPartParser]

    psq_rules = {
        ('list', 'retrieve'): [Rule([IsAuthenticated])]
    }


@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='Optional query parameter to get the message history of a specific user',
            required=False, type=int
        )
    ]
)
class MessageViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        queryset = Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user),
        ).prefetch_related('message_files')
        if user_id is not None:
            queryset = Message.objects.filter(
                Q(sender=self.request.user, recipient_id=user_id)
                |
                Q(sender_id=user_id, recipient=self.request.user)
            ).prefetch_related('message_files')
        return queryset


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser]

    @extend_schema(description='Get user data', methods=["GET"])
    @action(detail=False)
    def get_profile(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update user data', methods=["PUT"])
    @action(detail=False, methods=['PUT'])
    def update_profile(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update user notification', methods=["PUT"])
    @action(detail=False, methods=['PUT'], serializer_class=UserNotificationSerializer)
    def update_notification(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Switch calls and messages per agent', methods=["PUT"])
    @action(detail=False, methods=['PUT'], serializer_class=UserPerAgentSerializer)
    def switch_to_agent(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAgentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAgentSerializer

    @extend_schema(description='Get agent data', methods=["GET"])
    @action(detail=False)
    def get_agent(self, request):
        obj = get_object_or_404(Contact, user=request.user)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update agent data', methods=["PUT"])
    @action(detail=False, methods=['PUT'])
    def update_agent(self, request):
        obj = get_object_or_404(Contact, user=request.user)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    @extend_schema(description='Get subscription', methods=['GET'])
    @action(detail=False)
    def get_subscription(self, request):
        obj = get_object_or_404(Subscription, user=request.user)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Activate not active subscription', methods=['PUT'])
    @action(detail=False, methods=['PUT'])
    def active_subscription(self, request):
        obj = get_object_or_404(
            Subscription,
            user=request.user,
            is_active=False
        )
        obj.date_end = get_range_month().date()
        obj.is_active = True
        obj.is_auto_renewal = True
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Renew your subscription', methods=['PUT'])
    @action(detail=False, methods=['PUT'])
    def update_subscription(self, request):
        obj = get_object_or_404(
            Subscription,
            user=request.user,
            is_active=True
        )
        obj.date_end = get_range_month(obj.date_end)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Enable or disable auto-renewal of a subscription', methods=['PUT'])
    @action(
        detail=False,
        methods=['PUT'],
        serializer_class=UserAutoRenewalSubscriptionSerializer,
        parser_classes=[JSONParser]

    )
    def auto_renewal_subscription(self, request):
        obj = get_object_or_404(Subscription, user=request.user)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListViewSet(PsqMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_blacklist']
    search_fields = ['id', 'first_name', 'last_name', 'phone', 'email']

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False, is_developer=False)
        return queryset


@extend_schema(
    methods=['POST', "DELETE"],
    parameters=[
        OpenApiParameter(
            name='announcement_id',
            description='Required query parameter to announcement or remove an ad to favorites',
            required=True, type=int
        )
    ]
)
class FavoritesAnnouncementView(mixins.CreateModelMixin,
                                GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoritesAnnouncementSerializer
    queryset = User.objects.all()

    @extend_schema(description='Get user data', methods=["GET"])
    @action(detail=False)
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(description='Get user data', methods=['DELETE'])
    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        announcement_id = request.query_params.get('announcement_id')
        if Announcement.objects.filter(id=announcement_id).exists():
            obj = get_object_or_404(Announcement, id=announcement_id)
            request.user.favorites_announcement.remove(obj)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['POST', "DELETE"],
    parameters=[
        OpenApiParameter(
            name='residential_complex_id',
            description='Required query parameter to add or remove an residential complex to favorites',
            required=True, type=int
        )
    ]
)
class FavoritesResidentialComplexView(mixins.CreateModelMixin,
                                      GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoritesResidentialComplexSerializer
    queryset = User.objects.all()

    @extend_schema(description='Get user data', methods=["GET"])
    @action(detail=False)
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(description='Get user data', methods=['DELETE'])
    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        residential_complex_id = request.query_params.get('residential_complex_id')
        if ResidentialComplex.objects.filter(id=residential_complex_id).exists():
            obj = get_object_or_404(ResidentialComplex, id=residential_complex_id)
            request.user.favorites_residential_complex.remove(obj)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
