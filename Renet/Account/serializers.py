from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


