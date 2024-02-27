import jwt
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager
from django.conf import settings
from datetime import datetime, timedelta

class Account(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(_("username"), max_length=50, unique=True)
    first_name = models.CharField(_("first_name"), max_length=50)
    last_name = models.CharField(_("last_name"), max_length=50)
    email = models.EmailField(_("email"), unique=True, max_length=254)
    password = models.CharField(_("password"), max_length=100)
    count_of_followers = models.IntegerField(
        _('count_of_followers'),
        default=0,
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password", "first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def token(self):
        
        return self._generate_jwt_token()
    
    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=5)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def __str__(self):
        return self.email
    

class Profile(models.Model):
    IMAGE_VALIDATOR = FileExtensionValidator(allowed_extensions=['JPG', 'JPEG'])

    user = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
    )
    picture = models.ImageField(
        'Picture',
        upload_to='profiles_pictures/images/%Y/%m/%d/',
        validators=[IMAGE_VALIDATOR,],
        null=True,
        blank=True,
    )
    banner = models.ImageField(
        'Banner',
        upload_to='profiles_pictures/images/%Y/%m/%d/',
        validators=[IMAGE_VALIDATOR,],
        null=True,
        blank=True,
    )
    description = models.TextField(
        'Description',
        max_length=255
    )
    friends = models.ManyToManyField(
        Account,
        related_name='frends',
        blank=True,
        verbose_name='Друзья'
    )
    age = models.DecimalField(
        'Age',
        decimal_places=0,
        max_digits=100,
    )
    # friends = models.ManyToManyField(
    #     Account, 
    #     on_delete=models.CASCADE,
    # )

    def __str__(self):
        return self.user

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Follower(models.Model):
    user = models.ForeignKey(
        Account,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    follower = models.ForeignKey(
        Account,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    created = models.DateTimeField(auto_now_add=True)


class FriendRequest(models.Model):
    SENT = 'sent'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = (
        (SENT, 'Sent'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )

    author = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='get_request_creator',
        verbose_name='Request author'
    )
    recipient = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='get_request_recipient',
        verbose_name='Request recipient'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=SENT,
    )
    created = models.DateTimeField(auto_now_add=True)

