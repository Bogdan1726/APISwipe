from rest_framework import serializers
from users.models import Contact
from .models import (
    ResidentialComplex, ResidentialComplexBenefits, RegistrationAndPayment
)


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


class ResidentialComplexSerializer(serializers.ModelSerializer):
    residential_complex_benefits = ResidentialComplexBenefitsSerializer()
    # registration_and_payment = RegistrationAndPaymentSerializer()
    sales_department = SalesDepartmentSerializer()

    class Meta:
        model = ResidentialComplex
        fields = [
            'name', 'description', 'commissioning_date', 'is_commissioning',
            'address', 'map_lat', 'map_lon', 'distance', 'ceiling_height', 'gas',
            'status', 'type_house', 'class_house', 'technology', 'territory',
            'communal_payments', 'heating', 'sewerage', 'water_service', 'user',
            'residential_complex_benefits', 'sales_department'
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        requests_user_id = self.context.get('request').user.id
        instance = ResidentialComplex.objects.create(
            **validated_data, user_id=requests_user_id
        )
        ResidentialComplexBenefits.objects.create(
            **validated_data.pop('residential_complex_benefits'),
            residential_complex=instance
        )
        # RegistrationAndPayment.objects.create(
        #     **validated_data['registration_and_payment'],
        #     residential_complex=instance
        # )
        Contact.objects.create(
            **validated_data.pop('sales_department'),
            residential_complex=instance,
            type='Контакты агента'
        )
        return instance
