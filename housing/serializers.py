from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework import serializers
from users.models import Contact
from .services.base_64_data import get_base_64_images
from .validators import resident_complex_validator
from .models import (
    ResidentialComplex, ResidentialComplexBenefits, RegistrationAndPayment,
    ResidentialComplexNews, Document, GalleryResidentialComplex, Apartment
)

from drf_extra_fields.fields import Base64ImageField


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


class GalleryResidentialComplexSerializer2(serializers.ModelSerializer):
    list_pk = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = GalleryResidentialComplex
        fields = ['image', 'id', 'list_pk']
        read_only_fields = ['image']


class GalleryResidentialComplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryResidentialComplex
        fields = ['id', 'image']


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
                "image": get_base_64_images()
            }
        ),
    ],
)
class ResidentialComplexSerializer(serializers.ModelSerializer):
    benefits = ResidentialComplexBenefitsSerializer()
    registration_and_payment = RegistrationAndPaymentSerializer()
    sales_department_contact = SalesDepartmentSerializer()
    image = serializers.ListField(child=Base64ImageField(), required=False)
    gallery_residential_complex = GalleryResidentialComplexSerializer(many=True, read_only=True)

    class Meta:
        model = ResidentialComplex
        fields = [
            'id', 'name', 'description', 'commissioning_date', 'is_commissioning',
            'address', 'map_lat', 'map_lon', 'distance', 'ceiling_height', 'gas',
            'status', 'type_house', 'class_house', 'technology', 'territory',
            'communal_payments', 'heating', 'sewerage', 'water_service', 'user',
            'sales_department_contact', 'benefits', 'registration_and_payment',
            'gallery_residential_complex', 'image'
        ]
        read_only_fields = ['user', 'id']

    def create(self, validated_data):
        requests_user_id = self.context.get('request').user.id
        sales_department_contact_validated_data = validated_data.pop('sales_department_contact')
        registration_and_payment_validated_data = validated_data.pop('registration_and_payment')
        benefits_validated_data = validated_data.pop('benefits')
        image = validated_data.pop('image')
        instance = ResidentialComplex.objects.create(
            **validated_data, user_id=requests_user_id
        )
        ResidentialComplexBenefits.objects.create(
            **benefits_validated_data,
            residential_complex=instance
        )
        RegistrationAndPayment.objects.create(
            **registration_and_payment_validated_data,
            residential_complex=instance
        )
        Contact.objects.create(
            **sales_department_contact_validated_data,
            residential_complex=instance,
            type='Контакты агента'
        )
        images = image
        if images:
            for image in images:
                GalleryResidentialComplex.objects.create(
                    image=image,
                    residential_complex=instance,
                )
        return instance

    def update(self, instance, validated_data):
        sales_department_contact_validated_data = validated_data.pop('sales_department_contact')
        benefits_validated_data = validated_data.pop('benefits')
        registration_and_payment_validated_data = validated_data.pop('registration_and_payment')
        drag_and_drop_images = validated_data.pop('drag_and_drop_images')
        image = validated_data.pop('image')
        ResidentialComplexBenefits.objects.update(**benefits_validated_data)
        RegistrationAndPayment.objects.update(**registration_and_payment_validated_data)
        Contact.objects.update(**sales_department_contact_validated_data)
        images = image
        if drag_and_drop_images:
            for pk in drag_and_drop_images:
                GalleryResidentialComplex.objects.filter(id=pk).update(
                    order=drag_and_drop_images[pk]
                )
        if images:
            for image in images:
                GalleryResidentialComplex.objects.create(
                    image=image,
                    residential_complex=instance,
                )
        return super().update(instance, validated_data)


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
                'drag_and_drop_images': {
                    '25': '1',
                    '24': '3',
                    '26': '2'
                },
                "image": [

                ]
            }
        ),
    ],
)
class ResidentialComplexUpdateSerializer(ResidentialComplexSerializer):
    drag_and_drop_images = serializers.JSONField(required=False)

    class Meta(ResidentialComplexSerializer.Meta):
        fields = ResidentialComplexSerializer.Meta.fields + ['drag_and_drop_images']


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = [
            'plan', 'plan_floor', 'number', 'room', 'area', 'price_to_meter',
            'corpus', 'section', 'floor', 'riser', 'is_booked', 'decoration',
            'residential_complex', 'id', 'price'
        ]
        read_only_fields = ['id', 'price', 'is_booked']

    def create(self, validated_data):
        requests_user = self.context.get('request').user
        instance = Apartment.objects.create(**validated_data, user=requests_user)
        return instance


class ApartmentReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['is_booked']
