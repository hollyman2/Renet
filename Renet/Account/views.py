from django.contrib.auth import login, get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
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
from .models import Profile, FriendRequest
from posts.models import Report
from . import serializers

User = get_user_model()


def get_user(request):
    auth_header = str(request.headers.get('Authorization'))
    if auth_header is None:
        return Response(
            {'error': 'Токен не валиден или пользователь не авторизован'},
        )
    
    try:
        decoded_data = AccessToken(
            auth_header
        )
        user_id = decoded_data['user_id']
        user = User.objects.get(id=user_id)

        return user
    
    except: 

        return None
    

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


class MyProfileView(APIView):
    def get(self, request):
        user = get_user(request)
        user_serializer = serializers.SignupSerializer(user)
        if user is not None:
            try:
                profile = get_object_or_404(Profile, user=user)
                profile_serializer = serializers.ProfileSerializer(profile)

            except:

                return Response({'message': 'Create profile'})

            return Response(
                {
                    'user': user_serializer.data,
                    'profile': profile_serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "Вы должны сначала зарегестрироваться"})
    

class ProfileCreateView(APIView):

    def post(self, request):
        user = get_user(request=request)
        try:
            profile = get_object_or_404(Profile, user=user)
            return Response({"error": "У пользователя уже есть профиль"})
        except:
            serializer = serializers.ProfileSerializer()
            serializer = serializers.ProfileSerializer(
                serializer.create(
                    request.data,
                    user=user
                )
            )

            return Response(
                {'post': serializer.data},
                status=status.HTTP_201_CREATED
            )
            

class ProfileEditView(APIView):

    def post(self, request):
        user = get_user(request=request)
        try:
            profile = get_object_or_404(Profile, user=user)
            serializer = serializers.ProfileSerializer(profile)
       
            if user.id == serializer.data.get('user'):

                serializer = serializers.ProfileSerializer(
                    serializer.edit(
                        profile=profile,
                        data=request.data,
                    )
                )

                return Response(
                    {'profile': serializer.data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Вы не являетесь владельцем'}
                )
        except: 
            return Response(
                    {'error': 'Вы должны сначала создать'}
                )


class ProfileDetailView(APIView):
    def get(self, request, id):
        try:
            profile = get_object_or_404(Profile, id=id)
            serializer = serializers.ProfileSerializer(profile)

            return Response(
                    {'profile': serializer.data},
                    status=status.HTTP_200_OK
                )
        except:

            return Response(
                    {'error': 'Данного профиля не существует'}
                )
        
class SendFriendRequstView(APIView):
    def post(self, request, id):
        user = get_user(request=request)
        try:
            profile = get_object_or_404(Profile, id=id)
            profile_serializer = serializers.ProfileSerializer(profile)
            recipient_id = profile_serializer.data.get('user')
            if recipient_id == user.id:
                return Response(
                    {'error': 'Вы не можете отправлять заявку самому себе'}
                )

            recipient = get_object_or_404(User, id=recipient_id)
            try:
                friend_request = get_object_or_404(FriendRequest, author=user, recipient=recipient)
                return Response({"error": "Вы уже отправили заявку в друзья"})
            except:

                serializer = serializers.FriendRequestSerializer()
        
                serializer = serializers.FriendRequestSerializer(
                    serializer.create(
                        author=user,
                        recipient=recipient,
                    )
                )
        

                return Response(
                    {'friend request': serializer.data},
                    status=status.HTTP_201_CREATED
                )
        except:

            return Response(
                    {'error': 'Данного профиля не существует'}
                )

class ProfileFrendRequestsView(APIView):
    def get(self, request):
        user = get_user(request=request)
        try:
            
            friend_request = get_list_or_404(FriendRequest, recipient=user)
            serializer = serializers.FriendRequestSerializer(friend_request, many=True)
                
            
                
            return Response(
                    {'friend requests': serializer.data},
                    status=status.HTTP_200_OK
                )
        except:

            return Response(
                    {'message': 'Вы еще не получили ни одной заявки в друзья'}
                )
        
class AnswerFrendRequestsView(APIView):
    def post(self, request, id):
            user = get_user(request=request)
        # try:
            recipient_profile = get_object_or_404(Profile, user=user)
            friend_request = get_object_or_404(FriendRequest, recipient=user, id=id)
            author_profile = get_object_or_404(Profile, user=friend_request.recipient)
           
        
            if request.data.get('answer').lower() == 'yes':
        
                friend_request.status = 'accepted'
                friend_request.save()
                author_profile.friends.add(user)
                recipient_profile.friends.add(friend_request.author)

                return Response(
                    {'message': 'Вы приняли приглашение в друзья'}
                )
            if request.data.get('answer').lower() == 'no':

                friend_request.status = 'accepted'
                friend_request.save()

                return Response(
                    {'message': 'Вы отклонили заявку в друзья'}
                )
        # except:

        #     return Response(
        #             {'error': 'Ответ неккоректен либо данной заявки не существует '}
        #         )
    def get(self, request, id):
        return Response(
                    {'message': 'Ответьте на запрос в друзья в формате: yes or no'}
                )



class ReportProfileView(APIView):
    def post(self, request, id):

        author = get_user(request)
        profile = get_object_or_404(Profile, id=id)
        profile_serializer = serializers.ProfileSerializer(profile)
        recipient = get_object_or_404(User, id=profile_serializer.data.get('user'))
        try:
            report = get_object_or_404(Report, author=author, recipient=recipient)
            return Response(
                    {'message': 'Вы уже оправили жалобу на пользователя'}
                )
        except:
            serializer = serializers.ReportSerializer()
            serializer = serializers.ReportSerializer(
                serializer.create(
                    request.data,
                    author=author,
                    recipient=recipient,
                )
            )

            return Response(
                    {'report': serializer.data},
                    status=status.HTTP_201_CREATED
                )

