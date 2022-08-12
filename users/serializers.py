from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Notary, Subscription, Contact, MessageFile, Message
from .services.month_ahead import get_range_month

User = get_user_model()


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    # message_files = MessageFileSerializer(many=True, read_only=True)
    files = serializers.ListField(child=serializers.ImageField())

    class Meta:
        model = Message
        fields = ['message_files', 'files', 'text', 'sender', 'recipient', 'is_feedback']
        read_only_fields = ['recipient', 'sender', 'is_feedback']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_image', 'first_name', 'last_name', 'phone', 'email', 'notification', 'per_agent']


class NotarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Notary
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'profile_image']


class UserAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'phone', 'email']


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
