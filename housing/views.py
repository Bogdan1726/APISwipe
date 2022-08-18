from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import ResidentialComplexSerializer
from drf_psq import PsqMixin, Rule, psq

from .models import (
    ResidentialComplex
)
# Create your views here.


class ResidentialComplexViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplex.objects.all()

    # psq_rules = {
    #     ('list', 'retrieve'): [Rule([IsAuthenticated])],
    #     ('update', 'partial_update', 'destroy', 'create'): [Rule([IsAdminUser])]
    # }

