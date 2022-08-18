from rest_framework import serializers
from users.models import Contact
from .models import (
    ResidentialComplex, ResidentialComplexBenefits, RegistrationAndPayment
)
from collections import OrderedDict


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
    benefits = ResidentialComplexBenefitsSerializer()
    registration_and_payment = RegistrationAndPaymentSerializer()
    sales_department_contact = SalesDepartmentSerializer()

    class Meta:
        model = ResidentialComplex
        fields = [
            'id', 'name', 'description', 'commissioning_date', 'is_commissioning',
            'address', 'map_lat', 'map_lon', 'distance', 'ceiling_height', 'gas',
            'status', 'type_house', 'class_house', 'technology', 'territory',
            'communal_payments', 'heating', 'sewerage', 'water_service', 'user',
            'sales_department_contact', 'benefits', 'registration_and_payment'
        ]
        read_only_fields = ['user', 'id']

    def create(self, validated_data):
        requests_user_id = self.context.get('request').user.id
        sales_department_contact_validated_data = validated_data.pop('sales_department_contact')
        benefits_validated_data = validated_data.pop('benefits')
        registration_and_payment_validated_data = validated_data.pop('registration_and_payment')
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
        return instance

    def update(self, instance, validated_data):
        sales_department_contact_validated_data = validated_data.pop('sales_department_contact')
        benefits_validated_data = validated_data.pop('benefits')
        registration_and_payment_validated_data = validated_data.pop('registration_and_payment')
        ResidentialComplexBenefits.objects.update(**benefits_validated_data)
        RegistrationAndPayment.objects.update(**registration_and_payment_validated_data)
        Contact.objects.update(**sales_department_contact_validated_data)
        return super().update(instance, validated_data)
