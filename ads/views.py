from django_filters.rest_framework import DjangoFilterBackend
from drf_psq import PsqMixin, Rule
from rest_framework import viewsets, mixins, status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .permissions import IsMyAnnouncement, IsMyAdvertising
from .serializers import (
    AnnouncementSerializer, AnnouncementUpdateSerializer, AnnouncementComplaintSerializer,
    AnnouncementAdvertisingSerializer, AnnouncementModerationSerializer
)
from .models import (
    Announcement, Complaint, Advertising
)


# Create your views here.

@extend_schema(tags=['announcement'])
class AnnouncementViewSet(PsqMixin, viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_moderation_check']
    http_method_names = ['get', 'post', 'put', 'retrieve', 'delete']

    psq_rules = {
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser], AnnouncementUpdateSerializer),
            Rule([IsMyAnnouncement], AnnouncementUpdateSerializer)
        ]
    }

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

# class AnnouncementModerationViewSet(mixins.RetrieveModelMixin,
#                                     mixins.UpdateModelMixin,
#                                     mixins.ListModelMixin,
#                                     GenericViewSet):
#     serializer_class = AnnouncementAdvertisingSerializer
#     permission_classes = [IsAdminUser]
#     parser_classes = [JSONParser]
#
#     def get_queryset(self):
#         queryset = Announcement.objects.filter(is_moderation_check=False)
#         return queryset
