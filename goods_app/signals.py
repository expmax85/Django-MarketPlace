from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from taggit.models import Tag

from goods_app.models import ProductComment, ProductCategory, Product, Specifications, ProductRequest


@receiver(post_save, sender=ProductComment)
def comment_post_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    product_id = kwargs['instance'].product_id
    cache.delete('reviews:{}'.format(product_id))


@receiver(pre_delete, sender=ProductComment)
def comment_post_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    product_id = kwargs['instance'].product_id
    cache.delete('reviews:{}'.format(product_id))


@receiver(post_save, sender=ProductCategory)
def category_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    cache.delete_many(['categories:all', 'random_categories:all'])


@receiver(pre_delete, sender=ProductCategory)
def category_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    instance = kwargs['instance']
    instance.image.delete()
    instance.icon.delete()
    cache.delete_many(['categories:all', 'random_categories:all'])


@receiver(post_save, sender=Product)
def product_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    cache.delete_many(['tags:all', 'specifications:all', 'base_products:all'])


@receiver(pre_delete, sender=Product)
def product_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    instance = kwargs['instance']
    instance.image.delete()
    cache.delete_many(['tags:all', 'specifications:all', 'base_products:all'])


@receiver(post_save, sender=Tag)
def tags_reset_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    cache.delete('tags:all')


@receiver(pre_delete, sender=Tag)
def tags_reset_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    cache.delete('tags:all')


@receiver(post_save, sender=Specifications)
def specifications_cache_save_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    cache.delete('specifications:all')


@receiver(pre_delete, sender=Specifications)
def specifications_cache_del_handler(sender, **kwargs) -> None:
    """
    Signal for clearing cache
    """
    cache.delete('specifications:all')


@receiver(post_save, sender=ProductRequest)
def delete_instance(sender, **kwargs) -> None:
    """
    The signal for deleting decided ProductRequest instance
    """
    instance = kwargs.get('instance')
    if instance.is_published:
        instance.delete(keep_parents=True)
