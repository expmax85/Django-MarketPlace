from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BannersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banners_app'
    verbose_name = _('Banners control')

    def ready(self):
        from discounts_app import signals
