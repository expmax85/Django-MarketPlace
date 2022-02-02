from django.contrib.auth.models import User
from django.db import models


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
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=25, null=True)
    code = models.CharField(max_length=25, null=True)
    slug = models.SlugField(null=True)
    image = models.ImageField(null=True)
    description = models.TextField(max_length=255, null=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    comments = models.IntegerField(null=True)


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    author = models.CharField(max_length=25, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    content = models.TextField(max_length=255, null=True)
    added = models.DateTimeField(auto_now_add=True, null=True)
