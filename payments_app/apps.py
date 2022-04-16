from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class PaymentsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments_app'
    verbose_name = _('payments')
