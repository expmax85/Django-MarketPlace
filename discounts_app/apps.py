from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiscountsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discounts_app'
    verbose_name = _('Discounts control')

    def ready(self):
        from discounts_app import signals
