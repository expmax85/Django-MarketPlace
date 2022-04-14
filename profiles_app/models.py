from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

from settings_app.utils import check_image_size


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email: str, password: str, **extra_fields) -> 'User':
        """
        Create and save new user with email and password
        """
        if not email:
            raise ValueError(_('Email must be entering'))

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str) -> 'User':
        """
        Create superuser method
        """
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model
    """
    email = models.EmailField(verbose_name=_('email'), unique=True)
    username = models.CharField(verbose_name=_('username'), max_length=30, blank=True, null=True, default="")
    first_name = models.CharField(verbose_name=_('name'), max_length=30, blank=True, null=True, default="")
    last_name = models.CharField(verbose_name=_('surname'), max_length=30, blank=True, null=True, default="")
    phone = models.CharField(verbose_name=_('phone number'), max_length=16)
    date_joined = models.DateTimeField(verbose_name=_('registered'), auto_now_add=True)
    is_staff = models.BooleanField(verbose_name=_('is_staff'), default=False)
    is_active = models.BooleanField(verbose_name=_('is_active'), default=True)
    is_superuser = models.BooleanField(verbose_name=_('is_superuser'), default=False)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to='avatars/', null=True, blank=True)
    city = models.CharField(verbose_name=_('city'), max_length=40, null=True, blank=True, default="")
    address = models.CharField(verbose_name=_('address'), max_length=70, null=True, blank=True, default="")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        if self.username:
            return str(self.username)
        else:
            return str(self.email)

    def is_member(self, group_name: str) -> bool:
        """
        Method for checking membership in a group
        """
        try:
            if self.groups.filter(name=group_name):
                return True
        except ValueError:
            return False
        return False

    def save(self, *args, **kwargs) -> None:
        """
        Method overridden to remove old files and add permissions
        """
        check_image_size(self.avatar)
        if self.pk is not None:
            old_self = User.objects.get(pk=self.pk)
            if old_self.avatar and self.avatar != old_self.avatar:
                old_self.avatar.delete(False)
        super(User, self).save(*args, **kwargs)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'profiles'
        permissions = [
            ('Sellers', 'can sell'),
            ('Content_manager', 'app management'),
        ]
