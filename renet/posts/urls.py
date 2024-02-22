from django.urls import path
from posts import views

app_name = 'posts'

urlpatterns = [
    path('like/', views.LikeAPIView.as_view(), name='like')
]
