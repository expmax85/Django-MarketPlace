from django.db import models
from django.db.models import F, Sum
from profiles_app.models import User
from stores_app.models import SellerProduct
from profiles_app.models import User


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

    @property
    def total_sum(self):
        total = self.order_products.aggregate(total=Sum(F('position_price') * F('quantity')))['total']
        return total


class OrderProduct(models.Model):
    """
    Модель товара в заказе
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    seller_product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE, related_name='order_products')
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(null=True)

    @property
    def position_price(self):
        # final_price = get_discounted_price(self)   Получение цены со скидкой из сервиса скидок.
        # Пока цена магазина. Название метода получения цкны со скидкой пока условное
        return self.seller_product.price
