from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_psq import PsqMixin, Rule, psq

from .models import Notary, Contact, Subscription, Message
from .serializers import NotarySerializer, UserProfileSerializer, UserAgentSerializer, UserSubscriptionSerializer, \
    MessageSerializer
from .services.month_ahead import get_range_month

User = get_user_model()


# Create your views here.

class MessageViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Message.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, is_feedback=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotaryViewSet(PsqMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = NotarySerializer
    queryset = Notary.objects.all()

    psq_rules = {
        ('list', 'retrieve'): [Rule([IsAuthenticated]), serializer_class]
    }


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(description='Get user data', methods=["GET"])
    @action(detail=False)
    def get_profile(self, request):
        obj = get_object_or_404(User, id=request.user.id)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description='Update user data', methods=["POST"])
    @action(detail=False, methods=['POST'])
    def update_profile(self, request):
        obj = get_object_or_404(User, id=request.user.id)
        serializer = self.serializer_class(obj, request.data, partial=True)
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
