from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_psq import PsqMixin, Rule
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from users.permissions import IsDeveloper
from .permissions import IsMyResidentialComplex, IsMyResidentialComplexObject
from .serializers import (
    ResidentialComplexSerializer, ResidentialComplexNewsSerializer,
    ResidentialComplexDocumentSerializer, UserFavoritesResidentialComplexSerializer
)
from .models import (
    ResidentialComplex, ResidentialComplexNews, Document
)

User = get_user_model()


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


@extend_schema(tags=['residential-complex-favorites'])
@extend_schema(
    methods=['POST', "DELETE"],
    parameters=[
        OpenApiParameter(
            name='residential_complex_id',
            description='Required query parameter to add or remove an residential complex to favorites',
            required=True, type=int
        )
    ]
)
class FavoritesResidentialComplexViewSet(mixins.CreateModelMixin,
                                         GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoritesResidentialComplexSerializer
    queryset = User.objects.all()

    @extend_schema(description='Get user data', methods=["GET"])
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

    @extend_schema(description='Get user data', methods=['DELETE'])
    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        residential_complex_id = request.query_params.get('residential_complex_id')
        if ResidentialComplex.objects.filter(id=residential_complex_id).exists():
            obj = get_object_or_404(ResidentialComplex, id=residential_complex_id)
            request.user.favorites_residential_complex.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
