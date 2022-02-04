from django.contrib.auth import get_user_model
from django.db import models
from stores_app.models import SellerProduct


User = get_user_model()

class Order(models.Model):
    """
    Модель заказа
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='orders')
    delivery = models.CharField(max_length=25, null=True)
    city = models.CharField(max_length=25, null=True)
    address = models.TextField(max_length=255, null=True)
    #  payment_method  TODO определить
    #  status  TODO определить. Например: корзина, оформленный заказ, оплаченный заказ
    created = models.DateTimeField(auto_now_add=True, null=True)


class OrderProduct(models.Model):
    """
    Модель товара в заказе
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    seller_product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE, related_name='order_products')
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(null=True)
