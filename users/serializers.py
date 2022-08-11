from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Notary, Subscription, Contact

User = get_user_model()


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
        fields = '__all__'


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
