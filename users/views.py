from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_psq import PsqMixin, Rule, psq

from .models import Notary, Contact, Subscription
from .serializers import NotarySerializer, UserProfileSerializer, UserAgentSerializer, UserSubscriptionSerializer
from .services.month_ahead import get_range_month

User = get_user_model()


# Create your views here.

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
        obj = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update user data', methods=["POST"])
    @action(detail=False, methods=['POST', 'GET'])
    def update_profile(self, request):
        instance = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(instance, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAgentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAgentSerializer

    @extend_schema(description='Get agent data', methods=["GET"])
    @action(detail=False)
    def get_agent(self, request):
        obj, created = Contact.objects.get_or_create(
            user=request.user,
            type='Контакты агента',
        )
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update agent data', methods=["GET"])
    @action(detail=False, methods=['POST'])
    def update_agent(self, request):
        instance = Contact.objects.get(user=request.user)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    @extend_schema(methods=['GET'], description='subscription')
    @action(detail=False, methods=['GET'])
    def create_subscription(self, request):
        obj, created = Subscription.objects.get_or_create(user=request.user)
        if created:
            obj.date_end = get_range_month().date()
            obj.save()
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(description='Get subscription', methods=['GET'])
    @action(detail=False)
    def get_subscription(self, request):
        obj = get_object_or_404(Subscription, user=request.user)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(methods=['POST'], description='Pay subscription')
    @action(detail=False, methods=['POST'])
    def update_subscription(self):
        # instance = Contact.objects.get(user=request.user)
        # serializer = self.serializer_class(instance, data=request.data, partial=True)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        return Response(status=status.HTTP_200_OK)
