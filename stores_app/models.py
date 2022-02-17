from typing import Callable

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse

from goods_app.models import Product
from discounts_app.models import Discount


User = get_user_model()


class Seller(models.Model):
    """
    Store model
    """
    name = models.CharField(max_length=25, verbose_name=_('name'))
    slug = models.SlugField(verbose_name='slug', unique=True)
    description = models.TextField(max_length=255, null=True, blank=True, default="", verbose_name=_('description'))
    address = models.TextField(max_length=100, null=True, blank=True, default="", verbose_name=_('address'))
    icon = models.ImageField(upload_to='icons/', null=True, blank=True, verbose_name=_('icon'))
    email = models.EmailField(null=True, blank=True, default="", verbose_name='email')
    phone_valid = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=' '.join([str(_('Phone number must be entered in the format:')), '+999999999',
                                                   str(_('Up to 15 digits allowed.'))]))
    phone = models.CharField(max_length=25, validators=[phone_valid], null=True, blank=True, default="",
                             verbose_name=_('phone'))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller', verbose_name=_('owner'))

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self) -> Callable:
        return reverse('stores-polls:store_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _('store')
        verbose_name_plural = _('stores')


class SellerProduct(models.Model):
    """
    Seller product model
    """
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='seller_products',
        verbose_name=_('seller')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='seller_products',
        verbose_name=_('product')
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name='seller_products',
        verbose_name=_('discount')
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price_after_discount'))
    quantity = models.IntegerField(verbose_name=_('quantity'))

    def __str__(self):
        return f'{self.product} in {self.store}'

    class Meta:
        verbose_name = _('product in shop')
        verbose_name_plural = _('products in shop')
