from allauth.account.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework import serializers
from .models import (
    Notary, Subscription, Contact, MessageFile, Message, Filter
)

User = get_user_model()


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = [
            'id', 'status_house', 'district', 'microdistrict', 'rooms',
            'price_start', 'price_end', 'area_start', 'area_end',
            'type_housing', 'purpose', 'payment_options', 'state',
        ]
        read_only_fields = ['user']

    def validate(self, data):
        if 'area_start' in data and data['area_start'] is not None:
            if 'area_end' in data and data['area_end'] is not None:
                if data['area_start'] >= data['area_end']:
                    raise serializers.ValidationError(
                        {'error_area': 'area_start >= area_end'}
                    )
        if 'price_start' in data and data['price_start'] is not None:
            if 'price_end' in data and data['price_end'] is not None:
                if data['price_start'] >= data['price_end']:
                    raise serializers.ValidationError(
                        {'error_price': 'price_start >= price_end'}
                    )
        return data

    def create(self, validated_data):
        requests_user_id = self.context.get('request').user.id
        if Filter.objects.filter(user_id=requests_user_id).count() >= 4:
            raise serializers.ValidationError(
                {'error_max_count_user_filter': 'The maximum count of saved filters is 4'}
            )
        return Filter.objects.create(**validated_data, user_id=requests_user_id)


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = ['file']


class MessageSerializer(serializers.ModelSerializer):
    file = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    message_files = MessageFileSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['file', 'text', 'message_files', 'sender', 'recipient', 'is_feedback']
        read_only_fields = ['sender', 'message_files']

    def create(self, validated_data):
        files = validated_data.pop('file') if 'file' in validated_data else None
        instance = Message.objects.create(
            **validated_data, sender=self.context.get('request').user
        )
        if files:
            for file in files:
                MessageFile.objects.create(file=file, message=instance)
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'email', 'profile_image',
            'notification', 'per_agent'
        ]
        read_only_fields = [
            'id', 'notification', 'per_agent'
        ]

    def update(self, instance, validated_data):
        if validated_data.get('email') != instance.email:
            EmailAddress.objects.filter(user=instance).update(
                email=validated_data.get('email')
            )
        return super().update(instance, validated_data)


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notification']


class UserPerAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['per_agent']


class NotarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Notary
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'profile_image']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example 1",
            value={
                "first_name": "Test",
                "last_name": "Test",
                "phone": "+380939804334",
                "email": "agent@example.com"
            },
        ),
        OpenApiExample(
            "Example 2",
            value={
                "first_name": "Test 2",
                "last_name": "Test 2",
                "phone": "0939804334",
                "email": "agent2@example.com"
            },
        ),
    ],
)
class UserAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'phone', 'email']
        read_only_fields = ['id']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'date_end', 'is_active', 'is_auto_renewal', 'user']
        read_only_fields = ['date_end', 'is_active', 'user', 'is_auto_renewal', 'id']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Enable",
            value={
                "is_auto_renewal": 'true'
            },
        ),
        OpenApiExample(
            "Disable",
            value={
                "is_auto_renewal": 'false'
            },
        ),
    ],
)
class UserAutoRenewalSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['is_auto_renewal']


class CustomLoginSerializer(LoginSerializer):
    username = None


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(
        max_length=150,
        min_length=2,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        min_length=2,
        required=True,
    )

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def save(self, request):
        user = super().save(request)
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'is_blacklist']
        read_only_fields = ['id', 'first_name', 'last_name', 'phone', 'email']
