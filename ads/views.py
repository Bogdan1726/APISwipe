from drf_psq import PsqMixin, Rule
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (
    AnnouncementSerializer, AnnouncementUpdateSerializer, AnnouncementComplaintSerializer,
    AnnouncementAdvertisingSerializer
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
    http_method_names = ['get', 'post', 'put', 'retrieve', 'delete']

    psq_rules = {
        ('update', 'destroy'): [
            Rule([IsAuthenticated], AnnouncementUpdateSerializer)
        ]
    }


@extend_schema(tags=['announcement-complaint'])
class AnnouncementComplaintViewSet(PsqMixin, viewsets.ModelViewSet):
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
class AnnouncementAdvertisingViewSet(PsqMixin, viewsets.ModelViewSet):
    queryset = Advertising.objects.all()
    serializer_class = AnnouncementAdvertisingSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]
    http_method_names = ['get', 'put', 'retrieve']

    psq_rules = {
        ('update', 'retrieve'): [
            Rule([IsAuthenticated])
        ]
    }
