from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_psq import PsqMixin, Rule
from rest_framework import viewsets, mixins, status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
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
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(
            name='announcement__residential_complex',
            description='Required query parameter (id residential complex) to get a list of apartments in '
                        'this residential complex',
            required=True, type=int
        )
    ]
)
class ApartmentViewSet(PsqMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
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

    def get_queryset(self):
        announcement__residential_complex = self.request.query_params.get('announcement__residential_complex')
        if announcement__residential_complex:
            queryset = Apartment.objects.filter(
                announcement__residential_complex=announcement__residential_complex
            )
            return queryset
        return Apartment.objects.all()


@extend_schema(tags=['announcement'])
class AnnouncementViewSet(PsqMixin, viewsets.ModelViewSet):
    serializer_class = AnnouncementListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnnouncementFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    psq_rules = {
        ('create',): [Rule([IsAuthenticated], AnnouncementSerializer)],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser], AnnouncementUpdateSerializer),
            Rule([IsMyAnnouncement], AnnouncementUpdateSerializer)
        ]
    }

    def get_queryset(self):
        return Announcement.objects.filter(is_moderation_check=True).select_related(
            'creator', 'residential_complex', 'advertising', 'announcement_apartment'
        ).prefetch_related('favorite_announcement', 'gallery_announcement').order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        residential_complex_queryset = (
            ResidentialComplex.objects.prefetch_related(
                'gallery_residential_complex', 'favorite_complex'
            )
        )
        residential_complex_serializer = ResidentialComplexListSerializer(
            residential_complex_queryset, many=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            data=serializer.data + residential_complex_serializer.data, status=status.HTTP_200_OK
        )


@extend_schema(tags=['announcement-moderation'])
class AnnouncementModerationViewSet(mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.ListModelMixin,
                                    GenericViewSet):
    serializer_class = AnnouncementModerationSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put']

    def get_queryset(self):
        return Announcement.objects.filter(is_moderation_check=True).prefetch_related(
            'gallery_announcement'
        )


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
