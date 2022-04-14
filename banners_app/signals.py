from django.db.models.signals import pre_delete
from django.dispatch import receiver

from banners_app.models import Banner


@receiver(pre_delete, sender=Banner)
def product_discount_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    instance = kwargs['instance']
    instance.image.delete()
