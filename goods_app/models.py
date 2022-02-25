from django.contrib.auth import get_user_model
from django.db import models

from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

User = get_user_model()


class ProductCategory(MPTTModel):
    """
    Модель категории товаров
    """
    name = models.CharField(
        max_length=25,
        null=True,
        verbose_name=_('product_category')
    )
    slug = models.SlugField(null=True, verbose_name=_('product_category_slug'))
    description = models.TextField(max_length=255, null=True, verbose_name=_('product_category_description'))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('product categories')
        verbose_name = _('product category')

    class MPTTMeta:
        order_insertion_by = ['name']


class Product(models.Model):
    """
    Модель товара
    """
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('good_category'),
    )
    name = models.CharField(max_length=25, null=True, verbose_name=_('product_name'))
    code = models.CharField(max_length=25, null=True, verbose_name=_('product_code'))
    slug = models.SlugField(null=True, db_index=True, verbose_name=_('product_slug'))
    image = models.ImageField(null=True, blank=True, verbose_name=_('product_image'))
    description = models.TextField(max_length=255, null=True, verbose_name=_('product_description'))
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('average_price'))
    comments = models.IntegerField(null=True, verbose_name=_('amount_of_comments'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    author = models.CharField(max_length=25, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    content = models.TextField(max_length=255, null=True)
    added = models.DateTimeField(auto_now_add=True, null=True)
