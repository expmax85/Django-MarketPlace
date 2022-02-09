from django.db import models
from goods_app.models import Product
from discounts_app.models import Discount


class Seller(models.Model):
    """
    Модель магазина
    """
    name = models.CharField(max_length=25, null=True, verbose_name='name')
    slug = models.SlugField(null=True, verbose_name='slug')
    description = models.TextField(max_length=255, null=True, verbose_name='description')
    address = models.TextField(max_length=255, null=True, verbose_name='address')
    email = models.EmailField(null=True, name='email')
    phone = models.CharField(max_length=25, null=True, verbose_name='phone')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'store'
        verbose_name_plural = 'stores'


class SellerProduct(models.Model):
    """
    Модель товара в магазине
    """
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='seller_products',
        verbose_name='seller'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='seller_products',
        verbose_name='product'
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name='seller_products',
        verbose_name='discount'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='price')
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='price_after_discount')
    quantity = models.IntegerField(verbose_name='quantity')

    def __str__(self):
        return f'{self.product} in {self.seller}'

    class Meta:
        verbose_name = 'product in shop'
        verbose_name_plural = 'products in shop'
