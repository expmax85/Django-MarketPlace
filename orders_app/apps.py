from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class OrdersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders_app'
    verbose_name = _('Purchase and carts')
