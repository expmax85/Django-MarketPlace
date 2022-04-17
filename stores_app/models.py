import os
from typing import Callable, Dict

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse

from goods_app.models import Product
from settings_app.utils import check_image_size

User = get_user_model()


class Seller(models.Model):
    """
    Store model
    """
    name = models.CharField(max_length=50, verbose_name=_('name'))
    slug = models.SlugField(verbose_name='slug', unique=True)
    description = models.TextField(max_length=2550, null=True, blank=True, default="", verbose_name=_('description'))
    address = models.TextField(max_length=100, null=True, blank=True, default="", verbose_name=_('address'))
    icon = models.ImageField(upload_to='icons/', null=True, verbose_name=_('icon'))
    email = models.EmailField(null=True, blank=True, default="", verbose_name='email')
    phone = models.CharField(max_length=16, null=True, blank=True, default="",
                             verbose_name=_('phone'))
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='seller',
                              verbose_name=_('owner'))

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> Callable:
        return reverse('stores-polls:store-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs) -> None:
        check_image_size(self.icon)
        if self.pk is not None:
            old_self = Seller.objects.get(pk=self.pk)
            if old_self.icon and self.icon != old_self.icon:
                old_self.icon.delete(False)
        super(Seller, self).save(*args, **kwargs)

    @property
    def icon_url(self):
        if self.icon and hasattr(self.icon, 'url'):
            return self.icon.url

    class Meta:
        verbose_name = _('store')
        verbose_name_plural = _('stores')
        db_table = 'sellers'


class SellerProduct(models.Model):
    """
    Seller product model
    """
    seller = models.ForeignKey(Seller,
                               on_delete=models.CASCADE,
                               related_name='seller_products',
                               verbose_name=_('seller')
                               )
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='seller_products',
                                verbose_name=_('product')
                                )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    quantity = models.IntegerField(verbose_name=_('quantity'))
    date_added = models.DateTimeField(verbose_name=_('date added'), auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.product} in {self.seller}'

    def serialize(self) -> Dict:
        return self.__dict__

    class Meta:
        verbose_name = _('product in shop')
        verbose_name_plural = _('products in shop')
        db_table = 'store_products'

    def get_absolute_url(self) -> Callable:
        return reverse('stores-polls:edit-seller-product', kwargs={'slug': self.seller.slug,
                                                                   'pk': self.id})

    # Pay attention to discounts
    @property
    def get_discount(self) -> QuerySet:
        """
        Get all related ProductDiscounts
        """
        return self.product_discounts.all()


class ProductImportFile(models.Model):
    """ Модель файла импорта товаров """

    file = models.FileField(upload_to='import/products')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_files')
    errors = models.IntegerField(default=0)
    warnings = models.IntegerField(default=0)
    log_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(default='In progress', blank=True, max_length=24)

    def filename(self):
        return os.path.basename(self.file.name)

class ImportOrder(models.Model):

    can_import = models.BooleanField(default=True)
