from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Account
    path('accounts/', include('Account.urls', namespace='accounts')),
    # posts
    path('posts/', include('posts.urls', namespace='posts'))
]
