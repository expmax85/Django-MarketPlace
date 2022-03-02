from django.db.models.signals import post_save
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
        verbose_name='good_category',
    )
    name = models.CharField(max_length=25, null=True, verbose_name='product name')
    code = models.CharField(max_length=25, null=True, blank=True, verbose_name='product code')
    slug = models.SlugField(null=True, db_index=True, blank=True, verbose_name='product slug')
    image = models.ImageField(null=True, blank=True, verbose_name='product image')
    description = models.TextField(max_length=255, null=True, verbose_name='product description')
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='average price')
    rating = models.FloatField(null=True, blank=True, default=0, verbose_name='rating')
    is_published = models.BooleanField(verbose_name='is published', null=True, blank=True, default=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('goods-polls:product-detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        db_table = 'products'


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    author = models.CharField(verbose_name=_('author'), max_length=25, null=True)
    content = models.TextField(verbose_name=_('content'), max_length=255, null=True)
    added = models.DateTimeField(verbose_name=_('added'), auto_now_add=True, null=True)
    rating = models.IntegerField(verbose_name=_('rating'), null=True, blank=True)

    def __str__(self):
        return f'Comments for {str(self.product)}'

    class Meta:
        verbose_name = _('product comment')
        verbose_name_plural = _('product comments')
        db_table = 'comments'


class SpecificationsNames(models.Model):
    """ Все возможные характеристики """

    name = models.CharField(max_length=32, null=False)

    def __str__(self):
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

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _('specification')
        verbose_name_plural = _('specifications')
        db_table = 'specifications'


class ProductRequest(Product):
    product_ptr = models.OneToOneField(Product, on_delete=models.DO_NOTHING, parent_link=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.CharField(verbose_name=_('store'), max_length=30)
    notes = models.TextField(verbose_name=_('notes'), max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('new product')
        verbose_name_plural = _('new products')
        db_table = 'add_products'


def delete_Instance(sender, **kwargs) -> None:
    """
    The signal for removing icon Seller, when the store is deleting
    """
    instance = kwargs.get('instance')
    if instance.is_published:
        instance.delete(keep_parents=True)


post_save.connect(delete_Instance, ProductRequest)
