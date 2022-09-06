from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_psq import PsqMixin, Rule
from rest_framework import viewsets, mixins, status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from housing.models import ResidentialComplex
from .filters import AnnouncementFilter, ApartmentFilter
from .permissions import IsMyAnnouncement, IsMyAdvertising, IsMyApartment
from .serializers import (
    AnnouncementSerializer, AnnouncementUpdateSerializer, AnnouncementComplaintSerializer,
    AnnouncementAdvertisingSerializer, AnnouncementModerationSerializer,
    UserFavoritesAnnouncementSerializer, AnnouncementListSerializer, ResidentialComplexListSerializer,
    ApartmentSerializer, ApartmentUpdateSerializer,
)
from .models import (
    Announcement, Complaint, Advertising, Apartment
)

User = get_user_model()


# Create your views here.

@extend_schema(tags=['apartment'])
class ApartmentViewSet(PsqMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    queryset = Apartment.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    serializer_class = ApartmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApartmentFilter

    psq_rules = {
        ('update', 'partial_update'): [
            Rule([IsMyApartment], ApartmentUpdateSerializer),
            Rule([IsAdminUser], ApartmentUpdateSerializer)
        ]
    }


@extend_schema(tags=['announcement'])
class AnnouncementViewSet(PsqMixin, viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AnnouncementFilter
    search_fields = ['address']
    http_method_names = ['get', 'post', 'put', 'retrieve', 'delete']

    psq_rules = {
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser], AnnouncementUpdateSerializer),
            Rule([IsMyAnnouncement], AnnouncementUpdateSerializer)
        ]
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        residential_complex_queryset = (
            ResidentialComplex.objects.all()
        )
        residential_complex_serializer = ResidentialComplexListSerializer(
            residential_complex_queryset, many=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'residential_complex_data': residential_complex_serializer.data
        })

    @extend_schema(description='Confirm ads (check by moderator)', methods=['PUT'])
    @action(
        detail=True,
        methods=['PUT'],
        permission_classes=[IsAdminUser],
        serializer_class=AnnouncementModerationSerializer
    )
    def moderator_check(self, request, pk=None):
        obj = get_object_or_404(Announcement, id=pk)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['announcement-complaint'])
class AnnouncementComplaintViewSet(PsqMixin,
                                   mixins.CreateModelMixin,
                                   mixins.RetrieveModelMixin,
                                   mixins.DestroyModelMixin,
                                   mixins.ListModelMixin,
                                   GenericViewSet):
    queryset = Complaint.objects.all()
    serializer_class = AnnouncementComplaintSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]
    http_method_names = ['get', 'post', 'retrieve', 'delete']

    psq_rules = {
        ('create',): [
            Rule([IsAuthenticated])
        ]
    }


@extend_schema(tags=['announcement-advertising'])
class AnnouncementAdvertisingViewSet(PsqMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.UpdateModelMixin,
                                     GenericViewSet):
    queryset = Advertising.objects.all()
    serializer_class = AnnouncementAdvertisingSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]
    http_method_names = ['get', 'put', 'retrieve']

    psq_rules = {
        ('update', 'retrieve'): [
            Rule([IsMyAdvertising]),
            Rule([IsAdminUser])
        ]
    }


@extend_schema(tags=['announcement-favorites'])
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
class FavoritesAnnouncementViewSet(mixins.CreateModelMixin,
                                   GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoritesAnnouncementSerializer
    queryset = User.objects.all()

    @extend_schema(description='Get favorites apartments', methods=["GET"])
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

    @extend_schema(description='Deleted apartments from favorites', methods=['DELETE'])
    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        announcement_id = request.query_params.get('announcement_id')
        if Announcement.objects.filter(id=announcement_id).exists():
            obj = get_object_or_404(Announcement, id=announcement_id)
            request.user.favorites_announcement.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
