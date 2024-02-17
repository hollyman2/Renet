from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

Account = get_user_model()


class SignupSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    def create(self, validated_data):
        user = Account.objects.create_user(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            username=validated_data.get('username'),
            password=validated_data.get('password'),
        )
        return user