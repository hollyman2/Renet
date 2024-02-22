from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from Account.models import Follower

Account = get_user_model()


class SignupSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'email',
            'first_name',
            'last_name',
            'username',
            'password'
        ]

    def create(self, validated_data):
        account = Account.objects.create_user(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            username=validated_data.get('username'),
            password=validated_data.get('password'),
        )
        return account


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128)

    def validate(self, attrs):
        validate_password(attrs.get('password'))
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        min_length=6,
        max_length=100
    )

    def validate(self, attrs):
        validate_password(attrs.get('password'))
        return super().validate(attrs)


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
    )

    def validate(self, attrs):
        email_validator = EmailValidator()
        email_validator(attrs.get('new_email'))
        return super().validate(attrs)


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['user', 'follower']