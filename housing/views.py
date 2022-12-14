from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
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
@extend_schema(methods=['GET'], description='Get specific residential complex. Permissions: IsAuthenticated')
@extend_schema(methods=['PUT'],
               description='Update residential complex. Permissions: [IsMyResidentialComplex, IsAdminUser]')
class ResidentialComplexViewSet(PsqMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                GenericViewSet):
    serializer_class = ResidentialComplexSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        return ResidentialComplex.objects.prefetch_related(
            'news', 'gallery_residential_complex', 'document',
            'residential_complex_announcement',
            'residential_complex_announcement__announcement_apartment'
        )

    psq_rules = {
        ('update', 'partial_update'): [
            Rule([IsAdminUser]),
            Rule([IsAuthenticated, IsMyResidentialComplex])
        ]
    }

    @extend_schema(description='Get my residential complex, Permissions: IsMyResidentialComplex', methods=["GET"])
    @action(detail=False, permission_classes=[IsMyResidentialComplex])
    def get_my_complex(self, request):
        obj = get_object_or_404(ResidentialComplex, user=request.user)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['residential-complex-news'])
@extend_schema(
    methods=['GET'], description='Get news for a specific residential complex. Permissions: IsAuthenticated'
)
@extend_schema(methods=['POST'], description='Create new news. Permissions: [IsAdminUser, IsDeveloper]')
@extend_schema(
    methods=['PUT', 'DELETE'],
    description='Update and delete news. Permissions: [IsAdminUser, IsMyResidentialComplexObject]'
)
class ResidentialComplexNewsViewSet(PsqMixin,
                                    mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    GenericViewSet):
    serializer_class = ResidentialComplexNewsSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResidentialComplexNews.objects.all()
    parser_classes = [MultiPartParser]
    http_method_names = ['get', 'post', 'put', 'delete']

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsAuthenticated, IsMyResidentialComplexObject])
        ]
    }

    @extend_schema(responses=status.HTTP_200_OK,
                   description='Delete news Permissions: [IsAdminUser, IsMyResidentialComplexObject]',
                   examples=[OpenApiExample('Example',
                                            value={'message': 'Delete news success', 'status': status.HTTP_200_OK})])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={
                'message': 'Delete news success',
                'status': status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['residential-complex-document'])
@extend_schema(
    methods=['GET'], description='Get documents for a specific residential complex. Permissions: IsAuthenticated'
)
@extend_schema(methods=['POST'], description='Create new document. Permissions: [IsAdminUser, IsDeveloper]')
@extend_schema(
    methods=['PUT', 'DELETE'],
    description='Update and delete document Permissions: [IsAdminUser, IsMyResidentialComplexObject]'
)
class ResidentialComplexDocumentViewSet(PsqMixin,
                                        mixins.CreateModelMixin,
                                        mixins.RetrieveModelMixin,
                                        mixins.UpdateModelMixin,
                                        mixins.DestroyModelMixin,
                                        GenericViewSet):
    serializer_class = ResidentialComplexDocumentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    parser_classes = [MultiPartParser]
    http_method_names = ['get', 'post', 'put', 'delete']

    psq_rules = {
        ('create',): [Rule([IsAdminUser | IsDeveloper])],
        ('update', 'partial_update', 'destroy'): [
            Rule([IsAdminUser]), Rule([IsAuthenticated, IsMyResidentialComplexObject])
        ]
    }

    @extend_schema(responses=status.HTTP_200_OK,
                   description='Delete document  Permissions: [IsAdminUser, IsMyResidentialComplexObject]',
                   examples=[OpenApiExample('Example',
                                            value={'message': 'Delete document success',
                                                   'status': status.HTTP_200_OK})])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={
                'message': 'Delete document success',
                'status': status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['residential-complex-favorites'], description='Add new complex in favorites')
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
@extend_schema(methods=['POST'], description='Permissions: IsAuthenticated')
class FavoritesResidentialComplexViewSet(mixins.CreateModelMixin,
                                         GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoritesResidentialComplexSerializer
    queryset = User.objects.all()

    @extend_schema(description='Get residential complex favorites, Permissions: IsAuthenticated', methods=["GET"])
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

    @extend_schema(responses=status.HTTP_200_OK,
                   description='Delete residential complex favorites, Permissions: IsAuthenticated',
                   methods=['DELETE'],
                   examples=[OpenApiExample('Example',
                                            value={'message': 'Delete residential-complex favorites success',
                                                   'status': status.HTTP_200_OK})]
                   )
    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        residential_complex_id = request.query_params.get('residential_complex_id')
        if ResidentialComplex.objects.filter(id=residential_complex_id).exists():
            obj = get_object_or_404(ResidentialComplex, id=residential_complex_id)
            if request.user.favorites_residential_complex.filter(id=obj.id).exists():
                request.user.favorites_residential_complex.remove(obj)
                return Response(
                    data={
                        'message': 'Delete residential-complex favorites success',
                        'status': status.HTTP_200_OK
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
