from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from stores_app.models import Seller, SellerProduct


@receiver(post_save, sender=Seller)
def seller_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    if kwargs['created']:
        user_id = kwargs['instance'].owner_id
        cache.delete('stores:{}'.format(user_id))
        cache.delete('stores:all')


@receiver(post_delete, sender=Seller)
def seller_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache and delete images
    """
    instance = kwargs.get('instance')
    instance.icon.delete(save=False)
    user_id = instance.owner_id
    cache.delete('stores:{}'.format(user_id))
    cache.delete('stores:all')


@receiver(post_save, sender=SellerProduct)
def seller_product_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    if kwargs['created']:
        user_id = kwargs['instance'].seller.owner_id
        cache.delete('owner_sp:{}'.format(user_id))
        cache.delete_many(['limited:all', 'hot_offers:all', 'products:all'])


@receiver(post_delete, sender=SellerProduct)
def seller_product_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    instance = kwargs.get('instance')
    user_id = instance.seller.owner_id
    cache.delete('owner_sp:{}'.format(user_id))
    cache.delete_many(['limited:all', 'hot_offers:all', 'products:all'])
