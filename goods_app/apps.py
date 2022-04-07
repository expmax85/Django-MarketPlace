from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class GoodsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'goods_app'
    verbose_name = _('Products management')

    def ready(self):
        from goods_app import signals
