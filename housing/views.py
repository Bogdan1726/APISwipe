from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from drf_psq import PsqMixin, Rule, psq
from users.permissions import IsDeveloper
from .filters import ApartmentFilter
from .permissions import IsMyResidentialComplex, IsMyResidentialComplexObject, IsMyApartment
from .serializers import (
    ResidentialComplexSerializer, ResidentialComplexNewsSerializer,
    ResidentialComplexDocumentSerializer, ApartmentSerializer,
    ApartmentReservationSerializer, ResidentialComplexUpdateSerializer
)
from .models import (
    ResidentialComplex, ResidentialComplexNews, Document, Apartment
)


# Create your views here.


@extend_schema(tags=['residential-complex'])
class ResidentialComplexViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplex.objects.all()
    parser_classes = [JSONParser]

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser], ResidentialComplexUpdateSerializer),
            Rule([IsMyResidentialComplex], ResidentialComplexUpdateSerializer)
        ]
    }


@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(
            name='complex_id',
            description='Required query parameter to receive news of a specific complex',
            required=True, type=int
        )
    ]
)
@extend_schema(tags=['residential-complex-news'])
class ResidentialComplexNewsViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexNewsSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplexNews.objects.all()
    parser_classes = [MultiPartParser]

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsMyResidentialComplexObject])
        ]
    }

    def get_queryset(self):
        complex_id = self.request.query_params.get('complex_id')
        queryset = ResidentialComplexNews.objects.filter(
            residential_complex_id=complex_id
        )
        return queryset


@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(
            name='complex_id',
            description='Required query parameter to receive documents of a specific complex',
            required=True, type=int
        )
    ]
)
@extend_schema(tags=['residential-complex-document'])
class ResidentialComplexDocumentViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ResidentialComplexDocumentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    parser_classes = [MultiPartParser]

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsMyResidentialComplexObject])
        ]
    }

    def get_queryset(self):
        complex_id = self.request.query_params.get('complex_id')
        queryset = Document.objects.filter(
            residential_complex_id=complex_id
        )
        return queryset


@extend_schema(tags=['apartment'])
class ApartmentViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = ApartmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Apartment.objects.all()
    parser_classes = [MultiPartParser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApartmentFilter

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
