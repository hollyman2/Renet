from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpAPIView.as_view(), name='signup'),
    path('login/', views.LoginAPIView.as_view(), name='ogin'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', views.ActivateAccountAPIView.as_view(), name='activate'),
    path(
        'password-reset/',
        views.PasswordResetAPIView.as_view(),
        name='password_reset',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        views.PasswordResetConfirmAPIView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'email-change/',
        views.EmailChangeAPIView.as_view(),
        name='request-email-change'),
    path(
        'confirm-email-change/<uidb64>/<token>/',
        views.EmailChangeConfirmAPIView.as_view(),
        name='email_change_confirm'
    ),
]
