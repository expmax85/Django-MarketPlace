from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ProductCategory(models.Model):
    """
    Модель категории товаров
    """
    name = models.CharField(max_length=25, null=True)
    slug = models.SlugField(null=True)
    description = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = 'product categories'


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
    name = models.CharField(max_length=25, null=True, verbose_name='product_name')
    code = models.CharField(max_length=25, null=True, verbose_name='product_code')
    slug = models.SlugField(null=True, db_index=True, verbose_name='product_slug')
    image = models.ImageField(null=True, blank=True, verbose_name='product_image')
    description = models.TextField(max_length=255, null=True, verbose_name='product_description')
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name='average_price')
    comments = models.IntegerField(null=True, verbose_name='amount_of_comments')
    rating = models.FloatField(null=True, blank=True, default=0, verbose_name='rating')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    author = models.CharField(verbose_name=_('author'),max_length=25, null=True)
    content = models.TextField(verbose_name=_('content'),max_length=255, null=True)
    added = models.DateTimeField(verbose_name=_('added'), auto_now_add=True, null=True)
    rating = models.IntegerField(verbose_name=_('rating'), null=True, blank=True)

    def __str__(self):
        return f'Comments for {str(self.product)}'

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
