from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class ProfilesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles_app'
    verbose_name = _('Customers and users')

    def ready(self):
        from profiles_app import signals
