from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.views import APIView

from . import serializers

User = get_user_model()


class SignUpAPIView(APIView):
    """
    API View для регистрации пользователя
    """
    def post(self, request):
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = default_token_generator.make_token(user)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = self.request.build_absolute_uri(
            reverse_lazy('accounts:activate', kwargs={'uidb64': uidb64, 'token': token})
        )

        subject = 'Активация учетной записи'
        message = (
            f'Пожалуйста, перейдите по ссылке для'
            f' активации вашей учетной записи: {activation_link}'
        )
        from_email = 'myyardverify@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return Response(
            {
                'email': serializer.data.get('email'),
                'first_name': serializer.data.get('first_name'),
                'last_name': serializer.data.get('last_name'),
                'username': serializer.data.get('username')
            },
            status=status.HTTP_200_OK
        )


class ActivateAccountAPIView(APIView):
    """
    API View для активации учетной записи пользователя.
    """

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
        else:
            return Response(
                {
                    "error": "Ссылка активации недействительна или истекла"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'email': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username
            },
            status=status.HTTP_200_OK
        )