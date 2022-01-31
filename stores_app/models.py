from django.db import models
from goods_app.models import Product
from discounts_app.models import Discount


class Seller(models.Model):
    """
    Модель магазина
    """
    name = models.CharField(max_length=25, null=True)
    slug = models.SlugField(null=True)
    description = models.TextField(max_length=255, null=True)
    address = models.TextField(max_length=255, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=25, null=True)


class SellerProduct(models.Model):
    """
    Модель товара в магазине
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seller_products')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='seller_products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
