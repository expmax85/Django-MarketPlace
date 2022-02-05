from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с введенным им email и паролем.
        """
        if not email:
            raise ValueError(_('Email must be entering'))

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create superuser method
        """
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name=_('email'), unique=True)
    first_name = models.CharField(verbose_name=_('name'), max_length=30, blank=True)
    last_name = models.CharField(verbose_name=_('surname'), max_length=30, blank=True)
    phone_valid = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=' '.join([str(_('Phone number must be entered in the format:')), '+999999999',
                                                   str(_('Up to 15 digits allowed.'))]))
    phone = models.CharField(verbose_name=_('phone number'), max_length=16, validators=[phone_valid],
                             null=True, blank=True)
    date_joined = models.DateTimeField(verbose_name=_('registered'), auto_now_add=True)
    is_staff = models.BooleanField(verbose_name=_('is_staff'), default=False)
    is_active = models.BooleanField(verbose_name=_('is_active'), default=True)
    is_superuser = models.BooleanField(verbose_name=_('is_superuser'), default=False)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to='avatars/',
                               null=True, blank=True)
    city = models.CharField(verbose_name=_('city'), max_length=40,
                            null=True, blank=True)
    address = models.CharField(verbose_name=_('address'), max_length=70,
                            null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.first_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

