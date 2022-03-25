from decimal import Decimal

from django.core.validators import RegexValidator
from django.db import models
from stores_app.models import SellerProduct
from profiles_app.models import User
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    """
    Модель заказа
    """
    DELIVERY_CHOICES = [
        ('reg', _('Regular')),
        ('exp', _('Express'))
    ]

    PAYMENT_CHOICES = [
        ('card', _('Bank Card')),
        ('cash', _('From random account')),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE,
                                 null=True,
                                 related_name='orders',
                                 verbose_name=_('customer'))
    fio = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('name and lastname'))

    phone_valid = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=' '.join([str(_('Phone number must be entered in the format:')), '+999999999',
                                                   str(_('Up to 15 digits allowed.'))]))
    phone = models.CharField(max_length=16, validators=[phone_valid],
                             null=True, blank=True, verbose_name=_('phone number'))

    email = models.EmailField(null=True, blank=True, verbose_name=_('email'))

    delivery = models.CharField(max_length=3,
                                choices=DELIVERY_CHOICES, default='reg', verbose_name=_('delivery'))

    payment_method = models.CharField(max_length=4,
                                      choices=PAYMENT_CHOICES,
                                      default='card',
                                      verbose_name=_('payment method'))

    city = models.CharField(max_length=25, null=True, blank=True, verbose_name=_('city'))
    address = models.TextField(max_length=255, null=True, blank=True, verbose_name=_('address'))

    in_order = models.BooleanField(default=False, verbose_name=_('In order'))
    paid = models.BooleanField(default=False, verbose_name=_('Order is payed'))

    ordered = models.DateTimeField(null=True, blank=True, verbose_name=_('Order placement date'))
    braintree_id = models.CharField(max_length=150, blank=True)

    @property
    def total_sum(self) -> Decimal:
        """Метод получения общей стоимости товаров в заказе"""
        total = Decimal(0.00)
        for product in self.order_products.all():
            total += product.seller_product.price * product.quantity
        return total

    @property
    def total_discounted_sum(self) -> Decimal:
        """Метод получения общей стоимости товаров в заказе со скидками"""
        total = Decimal(0.00)
        for product in self.order_products.all():
            total += product.final_price * product.quantity
        return total

    def final_total(self):
        return self.total_discounted_sum

    def __str__(self):
        return f"{_('Order')} №{self.id}"

    def name(self):
        return self.__str__()

    def __len__(self) -> int:
        """Метод получения количества товаров в заказе"""
        return len(self.order_products.all())


class OrderProduct(models.Model):
    """
    Модель товара в заказе
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_products'
    )
    seller_product = models.ForeignKey(
        SellerProduct,
        on_delete=models.CASCADE,
        related_name='order_products'
    )
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name=_('Guess discount price'))
    quantity = models.IntegerField(null=True, default=1,
                                   verbose_name=_('quantity'))

    def __str__(self):
        return f"{_('OrderProduct')} №{self.id}"

    def name(self):
        return self.__str__()


class ViewedProduct(models.Model):
    """ Модель просмотренного товара """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed', blank=True, null=True)
    session = models.CharField(max_length=100, blank=True)
    product = models.ForeignKey('stores_app.SellerProduct', on_delete=models.CASCADE, related_name='viewed_list')
    date = models.DateTimeField(auto_now=True)
