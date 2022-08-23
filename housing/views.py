from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

from users.permissions import IsDeveloper
from .permissions import IsMyResidentialComplex, IsMyResidentialComplexObject, IsMyApartment
from .serializers import ResidentialComplexSerializer, ResidentialComplexNewsSerializer, \
    ResidentialComplexDocumentSerializer, ApartmentSerializer, ApartmentReservationSerializer
from drf_psq import PsqMixin, Rule, psq

from .models import (
    ResidentialComplex, ResidentialComplexNews, Document, Apartment
)


# Create your views here.


class ResidentialComplexViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplex.objects.all()
    parser_classes = [JSONParser]

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsMyResidentialComplex])
        ]
    }


@extend_schema(tags=['complex-news'])
class ResidentialComplexNewsViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexNewsSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplexNews.objects.all()

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsMyResidentialComplexObject])
        ]
    }


@extend_schema(tags=['complex-document'])
class ResidentialComplexDocumentViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexDocumentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsMyResidentialComplexObject])
        ]
    }


@extend_schema(tags=['apartment'])
class ApartmentViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ApartmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Apartment.objects.all()

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsMyApartment])
        ]
    }

    @extend_schema(description='Reservation a apartment', methods=["PUT"])
    @action(detail=True, methods=['PUT'], serializer_class=ApartmentReservationSerializer)
    def reservation(self, request, pk):
        obj = get_object_or_404(Apartment, id=pk)
        serializer = self.serializer_class(
            obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
