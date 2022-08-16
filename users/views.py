from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_psq import PsqMixin, Rule, psq

from .models import (
    Notary, Contact, Subscription, Message, Filter
)
from .permissions import IsMyFilter
from .serializers import (
    NotarySerializer, UserProfileSerializer, UserAgentSerializer, UserSubscriptionSerializer,
    MessageSerializer, FilterSerializer
)
from .services.month_ahead import get_range_month

User = get_user_model()


# Create your views here.

class FilterViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = FilterSerializer
    permission_classes = [IsAuthenticated, IsMyFilter]

    psq_rules = {
        ('create', ): [Rule([IsAuthenticated])]
    }

    def get_queryset(self):
        queryset = Filter.objects.filter(user=self.request.user).select_related(
            'user'
        )
        return queryset


class MessageViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        queryset = Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user),
        ).prefetch_related('message_files')
        return queryset

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        queryset = Message.objects.filter(
            Q(sender=self.request.user, recipient_id=pk)
            |
            Q(sender_id=pk, recipient=self.request.user)
        ).prefetch_related('message_files')
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotaryViewSet(PsqMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = NotarySerializer
    queryset = Notary.objects.all()

    psq_rules = {
        ('list', 'retrieve'): [Rule([IsAuthenticated])]
    }


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(description='Get user data', methods=["GET"])
    @action(detail=False)
    def get_profile(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update user data', methods=["POST"])
    @action(detail=False, methods=['POST'])
    def update_profile(self, request):
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
        obj, created = Contact.objects.get_or_create(user=request.user, type='Контакты агента')
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update agent data', methods=["POST"])
    @action(detail=False, methods=['POST'])
    def update_agent(self, request):
        obj = get_object_or_404(Contact, user=request.user)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    @extend_schema(description='create subscription', methods=['POST'])
    @action(detail=False, methods=['POST'])
    def create_subscription(self, request):
        obj, created = Subscription.objects.get_or_create(user=request.user)
        if created:
            obj.date_end = get_range_month().date()
            obj.save()
            serializer = self.serializer_class(obj)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description='Get subscription', methods=['GET'])
    @action(detail=False)
    def get_subscription(self, request):
        obj = get_object_or_404(Subscription, user=request.user)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Renew your subscription', methods=['POST'])
    @action(detail=False, methods=['POST'])
    def update_subscription(self, request):
        obj = get_object_or_404(Subscription, user=request.user)
        obj.date_end = get_range_month(obj.date_end)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Cancel auto-renewal', methods=['POST'])
    @action(detail=False, methods=['POST'])
    def off_auto_renewal_subscription(self, request):
        obj = get_object_or_404(Subscription, user=request.user)
        if obj.is_auto_renewal:
            obj.is_auto_renewal = False
            obj.save()
            serializer = self.serializer_class(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


