from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class StoresAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stores_app'
    verbose_name = _('Stores and sellers')

    def ready(self):
        from stores_app import signals
