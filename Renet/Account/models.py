from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager
import jwt
from django.conf import settings
from datetime import datetime, timedelta



class Account(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(_("username"), max_length=50)
    first_name = models.CharField(_("username"), max_length=50)
    last_name = models.CharField(_("username"), max_length=50)
    email = models.EmailField(_("email"), unique=True, max_length=254)
    password = models.CharField(_("password"), max_length=50)
    is_active = models.BooleanField(default=True)
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
    
