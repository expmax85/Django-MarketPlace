from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from orders_app.models import Order, ViewedProduct, OrderProduct


@receiver(post_save, sender=Order)
def order_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    user_id = kwargs['instance'].customer_id
    cache.delete('user_orders:{}'.format(user_id))
    cache.delete('user_last_order:{}'.format(user_id))


@receiver(pre_delete, sender=Order)
def order_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    user_id = kwargs['instance'].customer_id
    cache.delete('user_orders:{}'.format(user_id))
    cache.delete('user_last_order:{}'.format(user_id))


@receiver(post_save, sender=ViewedProduct)
def viewed_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    user_id = kwargs['instance'].user_id
    cache.delete('viewed:{}'.format(user_id))


@receiver(pre_delete, sender=ViewedProduct)
def viewed_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    user_id = kwargs['instance'].user_id
    cache.delete('viewed:{}'.format(user_id))


@receiver(post_save, sender=OrderProduct)
def products_reset_cache_save_order_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    instance = kwargs['instance']
    if instance.order.paid:
        cache.delete('products:all')
