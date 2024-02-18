from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpAPIView.as_view(), name='signup'),
    path('active/', views.ActivateAccountAPIView.as_view(), name='activate')
]
