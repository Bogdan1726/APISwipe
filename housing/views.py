from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import ResidentialComplexSerializer

from .models import (
    ResidentialComplex
)
# Create your views here.


class ResidentialComplexViewSet(viewsets.ModelViewSet):
    serializer_class = ResidentialComplexSerializer
    permission_classes = [IsAdminUser]
    queryset = ResidentialComplex.objects.all()

