from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_psq import PsqMixin, Rule
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from users.permissions import IsDeveloper
from .permissions import IsMyResidentialComplex, IsMyResidentialComplexObject
from .serializers import (
    ResidentialComplexSerializer, ResidentialComplexNewsSerializer,
    ResidentialComplexDocumentSerializer
)
from .models import (
    ResidentialComplex, ResidentialComplexNews, Document
)


# Create your views here.


@extend_schema(tags=['residential-complex'])
class ResidentialComplexViewSet(PsqMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    serializer_class = ResidentialComplexSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplex.objects.all()
    parser_classes = [JSONParser]

    psq_rules = {
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]),
            Rule([IsMyResidentialComplex])
        ]
    }


@extend_schema(tags=['residential-complex-news'])
class ResidentialComplexNewsViewSet(PsqMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    GenericViewSet):
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


@extend_schema(tags=['residential-complex-document'])
class ResidentialComplexDocumentViewSet(PsqMixin,
                                        mixins.RetrieveModelMixin,
                                        mixins.UpdateModelMixin,
                                        mixins.DestroyModelMixin,
                                        GenericViewSet):
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
