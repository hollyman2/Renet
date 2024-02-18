from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.reverse import reverse_lazy
from rest_framework.views import APIView

from . import serializers

User = get_user_model()


class SignUpAPIView(APIView):

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
        message = (f'Пожалуйста, перейдите по ссылке для'
                   f' активации вашей учетной записи: {activation_link}')
        from_email = 'myyardverify@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)
        return render(self.request, 'users/signup-done.html')


class ActivateAccountAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(self.kwargs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, self.kwargs['token']):
            user.is_active = True
            user.save()

            login(request, user)
            return redirect('products:products_list')

        return super().get(request, *args, **kwargs)