from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Notary
from .serializers import NotarySerializer, ProfileSerializer

User = get_user_model()

# Create your views here.


class NotaryViewSet(viewsets.ModelViewSet):
    serializer_class = NotarySerializer
    queryset = Notary.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
