from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Notary, Subscription, Contact, MessageFile, Message, Filter
)

User = get_user_model()


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        if data['area_start'] >= data['area_end']:
            raise serializers.ValidationError(
                {'error_area': 'area_start >= area_end'}
            )
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
        requests_user = self.context.get('request').user
        files = validated_data.pop('file') if 'file' in validated_data else None
        instance = Message.objects.create(**validated_data, sender=requests_user)
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
