from typing import Callable

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager

User = get_user_model()


class ProductCategory(MPTTModel):
    """
    Модель категории товаров
    """
    name = models.CharField(
        max_length=25,
        null=True,
        verbose_name=_('category title')
    )
    slug = models.SlugField(verbose_name=_('slug'), unique=True)
    description = models.TextField(max_length=255, null=True, blank=True, verbose_name=_('description'))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    icon = models.ImageField(verbose_name=_('icon'))
    image = models.ImageField(verbose_name=_('image'))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = _('product categories')
        verbose_name = _('product category')

    class MPTTMeta:
        order_insertion_by = ['name']

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    @property
    def icon_url(self):
        if self.icon and hasattr(self.icon, 'url'):
            return self.icon.url

    def save(self, *args, **kwargs) -> Callable:
        """
        Method overridden to remove old files and add permissions
        """
        if self.pk is not None:
            old_self = ProductCategory.objects.get(pk=self.pk)
            if old_self.image and self.image != old_self.image:
                old_self.image.delete(False)
            if old_self.icon and self.icon != old_self.icon:
                old_self.icon.delete(False)
        return super(ProductCategory, self).save(*args, **kwargs)


class Product(models.Model):
    """
    Модель товара
    """
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='good_category',
    )
    name = models.CharField(max_length=100, verbose_name=_('product name'))
    code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('product code'))
    slug = models.SlugField(db_index=True, verbose_name=_('product slug'), unique=True)
    image = models.ImageField(verbose_name=_('product image'))
    description = models.TextField(max_length=2550, null=True, verbose_name=_('product description'))
    rating = models.FloatField(null=True, default=0, verbose_name=_('rating'))
    is_published = models.BooleanField(verbose_name=_('is published'), null=True, blank=True, default=True)
    tags = TaggableManager()
    limited = models.BooleanField(default=False, verbose_name=_('limited edition'))

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> Callable:
        return reverse('goods-polls:product-detail', kwargs={'slug': self.slug})

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        db_table = 'products'

    def save(self, *args, **kwargs) -> Callable:
        """
        Method overridden to remove old files and add permissions
        """
        if self.pk is not None:
            old_self = Product.objects.get(pk=self.pk)
            if old_self.image and self.image != old_self.image:
                old_self.image.delete(False)
        return super().save(*args, **kwargs)


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    author = models.CharField(verbose_name=_('author'), max_length=25, null=True)
    content = models.TextField(verbose_name=_('content'), max_length=255, null=True)
    added = models.DateTimeField(verbose_name=_('added'), auto_now_add=True, null=True)
    rating = models.IntegerField(verbose_name=_('rating'))

    def __str__(self) -> str:
        return f'Comments for {str(self.product)}'

    class Meta:
        verbose_name = _('product comment')
        verbose_name_plural = _('product comments')
        db_table = 'comments'


class SpecificationsNames(models.Model):
    """ Все возможные характеристики """

    name = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _('specification name')
        verbose_name_plural = _('specification names')
        db_table = 'specification_names'


class Specifications(models.Model):
    """ Модель Характеристики товара """

    value = models.CharField(max_length=32, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='specifications')
    current_specification = models.ForeignKey(SpecificationsNames, on_delete=models.CASCADE, blank=True, null=True,
                                              related_name='specifications')

    def __str__(self) -> str:
        return self.value

    class Meta:
        verbose_name = _('specification')
        verbose_name_plural = _('specifications')
        db_table = 'specifications'


class ProductRequest(Product):
    """
    Model for requesting to add new Product
    """
    product_ptr = models.OneToOneField(Product, on_delete=models.DO_NOTHING, parent_link=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.CharField(verbose_name=_('store'), max_length=30)
    notes = models.TextField(verbose_name=_('notes'), max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _('new product')
        verbose_name_plural = _('new products')
        db_table = 'add_products'
