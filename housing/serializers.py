from json import loads, dumps
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework import serializers
from ads.models import Announcement, Apartment
from users.models import Contact
from .services.base_64_data import get_base_64_images
from .validators import resident_complex_validator
from drf_extra_fields.fields import Base64ImageField
from .models import (
    ResidentialComplex, ResidentialComplexBenefits, RegistrationAndPayment,
    ResidentialComplexNews, Document, GalleryResidentialComplex
)

User = get_user_model()


class ResidentialComplexNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentialComplexNews
        fields = '__all__'

    def validate_residential_complex(self, value):
        request_user = self.context.get('request').user
        return resident_complex_validator(value, request_user)


class ResidentialComplexDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

    def validate_residential_complex(self, value):
        request_user = self.context.get('request').user
        return resident_complex_validator(value, request_user)


class ResidentialComplexBenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentialComplexBenefits
        fields = '__all__'
        read_only_fields = ['residential_complex']


class RegistrationAndPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationAndPayment
        fields = '__all__'
        read_only_fields = ['residential_complex']


class SalesDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'phone', 'email']


class GalleryResidentialComplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryResidentialComplex
        fields = ['id', 'image']


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = GalleryResidentialComplex
        fields = ['image', 'order']


class ImageOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = GalleryResidentialComplex
        fields = ['id', 'order']


class ApartmentComplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['id', 'corpus', 'is_booked', 'price_to_meter']


class AnnouncementComplexSerializer(serializers.ModelSerializer):
    announcement_apartment = ApartmentComplexSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ['announcement_apartment', 'area', 'price']


class UserIsBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'email', 'profile_image',
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example 1",
            value={
                "name": "Test",
                "description": "Test",
                "is_commissioning": 'true',
                "address": "test",
                "map_lat": "46.37668422515867",
                "map_lon": "30.721478800598362",
                "distance": 2500,
                "ceiling_height": 2.5,
                "gas": 'true',
                "status": "Квартиры",
                "type_house": "Многоквартирный",
                "class_house": "Элитный",
                "technology": "Монолитный каркас с керамзитно-блочным заполнением",
                "territory": "Закрытая охраняемая",
                "communal_payments": "Платежи",
                "heating": "Центральное",
                "sewerage": "Центральная",
                "water_service": "Центральное",
                "sales_department_contact": {
                    "first_name": "Юля",
                    "last_name": "Тест",
                    "phone": "+380955554433",
                    "email": "user@example.com"
                },
                "benefits": {
                    "playground": 'true',
                    "sportsground": 'true',
                    "parking": 'true',
                    "territory_protected": 'true'
                },
                "registration_and_payment": {
                    "formalization": "Юстиция",
                    "payment_options": "Ипотека",
                    "purpose": "Жилое помещение",
                    "contract_sum": "Неполная"
                },
                "images_order": [
                    {
                        "id": 0,
                        "order": 0
                    },
                ],
                "images": get_base_64_images()
            }
        ),
    ],
)
class ResidentialComplexSerializer(serializers.ModelSerializer):
    benefits = ResidentialComplexBenefitsSerializer()
    registration_and_payment = RegistrationAndPaymentSerializer()
    sales_department_contact = SalesDepartmentSerializer()
    user = UserIsBuilderSerializer(read_only=True)
    images = ImageSerializer(required=False, many=True, write_only=True)
    images_order = ImageOrderSerializer(many=True, write_only=True)
    gallery_residential_complex = GalleryResidentialComplexSerializer(many=True, read_only=True)
    news = ResidentialComplexNewsSerializer(many=True, read_only=True)
    document = ResidentialComplexDocumentSerializer(many=True, read_only=True)
    residential_complex_announcement = AnnouncementComplexSerializer(
        read_only=True, many=True
    )

    class Meta:
        model = ResidentialComplex
        fields = [
            'id', 'name', 'description', 'commissioning_date', 'is_commissioning',
            'address', 'map_lat', 'map_lon', 'distance', 'ceiling_height', 'gas',
            'status', 'type_house', 'class_house', 'technology', 'territory',
            'communal_payments', 'heating', 'sewerage', 'water_service', 'user',
            'sales_department_contact', 'benefits', 'registration_and_payment',
            'news', 'document', 'images', 'gallery_residential_complex',
            'images_order', 'residential_complex_announcement'
        ]
        read_only_fields = ['user', 'id']

    def update(self, instance, validated_data):
        sales_department_contact_validated_data = validated_data.pop('sales_department_contact')
        registration_and_payment_validated_data = validated_data.pop('registration_and_payment')
        benefits_validated_data = validated_data.pop('benefits')
        images_order_validate = validated_data.pop('images_order')
        images_validated_data = validated_data.pop('images')
        ResidentialComplexBenefits.objects.update(**benefits_validated_data)
        RegistrationAndPayment.objects.update(**registration_and_payment_validated_data)
        Contact.objects.update(**sales_department_contact_validated_data)
        if images_order_validate:
            list_images_id = []
            for data in loads(dumps(images_order_validate)):
                GalleryResidentialComplex.objects.filter(
                    id=int(data['id'])
                ).update(order=data['order'])
                list_images_id.append(int(data['id']))
            GalleryResidentialComplex.objects.exclude(
                residential_complex=instance, id__in=list_images_id
            ).delete()
        else:
            GalleryResidentialComplex.objects.filter(residential_complex=instance).delete()
        if images_validated_data:
            for valid_data in images_validated_data:
                GalleryResidentialComplex.objects.create(
                    **valid_data,
                    residential_complex=instance,
                )

        return super().update(instance, validated_data)


class FavoritesResidentialComplexSerializer(serializers.ModelSerializer):
    gallery_residential_complex = GalleryResidentialComplexSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = ResidentialComplex
        fields = ['id', 'name', 'address', 'gallery_residential_complex']


class UserFavoritesResidentialComplexSerializer(serializers.ModelSerializer):
    favorites_residential_complex = FavoritesResidentialComplexSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = User
        fields = ['favorites_residential_complex']

    def create(self, validated_data):
        residential_complex_id = self.context.get('request').query_params.get('residential_complex_id')
        request_user = self.context.get('request').user
        if residential_complex_id:
            if not ResidentialComplex.objects.filter(id=residential_complex_id).exists():
                raise serializers.ValidationError(
                    {
                        'error_announcement': 'Нет такого ЖК'
                    }
                )
            request_user.favorites_residential_complex.add(residential_complex_id)
        return request_user
