from django.contrib.auth import login, get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

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
    permission_classes = []
    authentication_classes = []

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Ссылка активации недействительна или истекла'}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Ссылка активации недействительна или истекла'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=email)

        if not user.is_active:
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
                {'message': 'На почту было отправлена инструкция по активации аккаунта'},
                status=status.HTTP_200_OK
            )

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Неверные учетные данные.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        response = Response()
        response.delete_cookie(
            'refresh_token',
            path='/api/token/refresh/'
        )
        response.data = {'message': 'Вы успешно вышли из системы.'}
        return response


class PasswordResetAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                password_reset_link = request.build_absolute_uri(
                    reverse_lazy(
                        'accounts:password_reset_confirm',
                        kwargs={'uidb64': uidb64, 'token': token}
                    )
                )

                subject = 'Сброс пароля'
                message = (
                    f'Пожалуйста, перейдите по ссылке для сброса вашего пароля:'
                    f' {password_reset_link}'
                )
                from_email = 'from@example.com'
                recipient_list = [user.email]

                send_mail(subject, message, from_email, recipient_list)
                return Response(
                    {
                        'message':
                            'Инструкции по сбросу пароля отправлены на вашу электронную почту.'
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    'error': 'Пользователь с таким адресом электронной почты не найден.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return Response({'message': 'Пожалуйста, введите новый пароль.'})
        else:
            return Response(
                {'error': 'Ссылка для сброса пароля недействительна или истекла.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = serializers.PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Пароль успешно сброшен.'})

            return Response(
                {'error': 'Ошибка сброса пароля.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailChangeAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request, *args, **kwargs):
        try:
            decoded_data = AccessToken(
                request.COOKIES.get('access_token')
            )
            user_id = decoded_data['user_id']
            user = User.objects.get(id=user_id)
        except TokenError:
            return Response(
                {'error': 'Токен не валиден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_email = request.data.get('new_email')
        serializer = serializers.EmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exteption=True)

        if not new_email:
            return Response(
                {
                    'error': 'Новый адрес электронной почты не предоставлен.'
                },
                status=400
            )

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.email))

        activation_link = request.build_absolute_uri(
            reverse_lazy(
                'accounts:email_change_confirm',
                kwargs={
                    'uidb64': uidb64,
                    'token': token
            })
        )

        subject = 'Подтверждение изменения электронной почты'
        message = f'Пожалуйста, перейдите по ссылке для подтверждения изменения вашей электронной почты: {activation_link}'
        from_email = 'myyardverify@gmail.com'
        recipient_list = [new_email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({
            'message':
                'Ссылка для подтверждения изменения электронной почты отправлена.'
        })


class EmailChangeConfirmAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            email = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(email=email)

            if default_token_generator.check_token(user, token):
                user.email = email
                user.save()
                return Response({'message': 'Ваш адрес электронной почты был успешно изменен.'})
            else:
                return Response({'error': 'Неверный токен или токен истек.'}, status=400)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
        ):
            return Response(
                {'error': 'Неверный запрос.'},
                status=400
            )


class AddFollowerAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, username, *args, **kwargs):
        follower = request.user
        user = User.objects.get(username=username)

        serializer = serializers.FollowerSerializer(
            data={
                'user': user,
                'follower': follower
            }
        )
        if serializer.is_valid():
            follower_user = serializer.validated_data['follower']
            if request.user != follower_user:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Вы не можете подписаться на самого себя."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)