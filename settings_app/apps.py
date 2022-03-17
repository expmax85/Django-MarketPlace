from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SettningsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = _('Site settings')
