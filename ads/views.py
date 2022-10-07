from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_psq import PsqMixin, Rule
from rest_framework import mixins, status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from housing.models import ResidentialComplex
from users.models import Filter
from users.serializers import FilterSerializer
from .filters import AnnouncementFilter, ApartmentFilter
from .permissions import IsMyAnnouncement, IsMyAdvertising, IsMyApartment
from .serializers import (
    AnnouncementSerializer, AnnouncementUpdateSerializer, AnnouncementComplaintSerializer,
    AnnouncementAdvertisingSerializer, AnnouncementModerationSerializer,
    UserFavoritesAnnouncementSerializer, AnnouncementListSerializer, ResidentialComplexListSerializer,
    ApartmentSerializer, AnnouncementRetrieveSerializer,
)
from .models import (
    Announcement, Complaint, Advertising, Apartment
)

User = get_user_model()


# Create your views here.

@extend_schema(tags=['announcement-feed'], description='Permission: IsAuthenticated')
class AnnouncementListViewSet(PsqMixin,
                              mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    serializer_class = AnnouncementListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnnouncementFilter
    queryset = Announcement.objects.all()

    psq_rules = {
        ('retrieve',): [Rule([IsAuthenticated], AnnouncementRetrieveSerializer)]
    }

    def get_queryset(self):
        return Announcement.objects.all().select_related(
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
        return Response({
            'data': serializer.data + residential_complex_serializer.data,
            'filters': FilterSerializer(
                Filter.objects.filter(user=request.user), many=True, read_only=True
            ).data
        },
            status=status.HTTP_200_OK
        )

    @extend_schema(description='Get my announcements, Permission: IsAuthenticated', methods=["GET"])
    @action(detail=False, serializer_class=AnnouncementRetrieveSerializer)
    def get_my_announcement(self, request):
        queryset = Announcement.objects.filter(creator=request.user).select_related(
            'creator', 'residential_complex', 'advertising', 'announcement_apartment'
        ).prefetch_related('favorite_announcement', 'gallery_announcement').order_by('id')
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['announcement'])
@extend_schema(methods=['POST'], description='Permissions: IsAuthenticated')
@extend_schema(methods=['PUT', 'DELETE'], description='Permissions: [IsMyAnnouncement, IsAdminUser]')
class AnnouncementViewSet(PsqMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Announcement.objects.all()
    http_method_names = ['post', 'put', 'delete']

    psq_rules = {
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser], AnnouncementUpdateSerializer),
            Rule([IsAuthenticated, IsMyAnnouncement], AnnouncementUpdateSerializer)
        ]
    }

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={
                'message': 'Delete announcement success',
                'status': status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['announcement-moderation'], description='Permissions: IsAdminUser')
class AnnouncementModerationViewSet(mixins.UpdateModelMixin,
                                    mixins.ListModelMixin,
                                    GenericViewSet):
    serializer_class = AnnouncementModerationSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put']

    def get_queryset(self):
        return Announcement.objects.filter(is_moderation_check=False).select_related(
            'advertising', 'announcement_apartment'
        ).prefetch_related('favorite_announcement', 'gallery_announcement').order_by('id')


@extend_schema(tags=['announcement-complaint'])
@extend_schema(methods=['POST'], description='Permissions: IsAuthenticated')
@extend_schema(methods=['GET', 'DELETE'], description='Permissions: IsAdminUser')
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={
                'message': 'Delete announcement-complaint success',
                'status': status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['announcement-advertising'], description='Permissions: [IsAdminUser, IsMyAdvertising]')
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
            Rule([IsAuthenticated, IsMyAdvertising]),
            Rule([IsAdminUser])
        ]
    }


@extend_schema(tags=['announcement-favorites'], description='Permissions: IsAuthenticated')
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

    @extend_schema(description='Get favorites apartments, Permissions: IsAuthenticated', methods=["GET"])
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(description='Deleted apartments from favorites, Permissions: IsAuthenticated', methods=['DELETE'])
    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        announcement_id = request.query_params.get('announcement_id')
        if Announcement.objects.filter(id=announcement_id).exists():
            obj = get_object_or_404(Announcement, id=announcement_id)
            if request.user.favorites_announcement.filter(id=obj.id).exists():
                request.user.favorites_announcement.remove(obj)
                return Response(
                    data={
                        'message': 'Delete announcement favorites success',
                        'status': status.HTTP_200_OK
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['apartment'])
@extend_schema(methods=['GET'], description='Permissions: IsAuthenticated')
@extend_schema(methods=['PUT'], description='Permissions: [IsMyApartment, IsAdminUser]')
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
    http_method_names = ['get', 'put']

    psq_rules = {
        ('update', 'partial_update'): [
            Rule([IsAuthenticated, IsMyApartment]),
            Rule([IsAdminUser])
        ]
    }

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='announcement__residential_complex',
                description='Required query parameter (id residential complex) to get a list of apartments in '
                            'this residential complex',
                required=True, type=int
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        announcement__residential_complex = self.request.query_params.get('announcement__residential_complex')
        if announcement__residential_complex:
            queryset = Apartment.objects.filter(
                announcement__residential_complex=announcement__residential_complex
            )
            return queryset
        return Apartment.objects.all()
