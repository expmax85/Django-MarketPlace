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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    author = models.CharField(max_length=25, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    content = models.TextField(max_length=255, null=True)
    added = models.DateTimeField(auto_now_add=True, null=True)
