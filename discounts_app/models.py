from typing import Callable

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from goods_app.models import ProductCategory
from stores_app.models import Seller, SellerProduct

TYPE_CHOICES = [
    ('p', _('Per cent')),
    ('f', _('Fixed amount')),
    ('fp', _('Fixed price')),
]

PRIORITY_CHOICES = [
    ('1', _('Low')),
    ('2', _('Medium')),
    ('3', _('High')),
]


class Discount(models.Model):
    """
    Абстрактная модель скидок
    """
    name = models.CharField(verbose_name=_("Title discount"), max_length=25, null=True)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), max_length=255,
                                   null=True, blank=True)
    type_of_discount = models.CharField(max_length=2, choices=TYPE_CHOICES,
                                        default='p', verbose_name=_('Discount type'))
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES,
                                default='1', verbose_name=_('Priority'))
    percent = models.FloatField(verbose_name=_("Percent"),
                                validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                default=0)
    amount = models.FloatField(verbose_name=_("Amount"),
                               validators=[MinValueValidator(0.0)],
                               default=0)
    fixed_price = models.FloatField(verbose_name=_("Fixed price"),
                                    validators=[MinValueValidator(0.0)],
                                    default=0)

    valid_from = models.DateTimeField(verbose_name=_("Valid from"), null=True, blank=True)
    valid_to = models.DateTimeField(verbose_name=_("Valid to"), null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Discount, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        constraints = (
            CheckConstraint(
                check=Q(percent__gte=0.0) & Q(percent__lte=100.0),
                name='discount_percent_range'),
            CheckConstraint(
                check=Q(amount__gte=0.0),
                name='discount_amount_value'),
        )


class ProductDiscount(Discount):
    """
    Модель товарной скидки
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,
                               related_name='product_discounts',
                               verbose_name=_('Seller'))
    seller_products = models.ManyToManyField(SellerProduct, related_name='product_discounts',
                                             verbose_name=_('Seller products'))
    set_discount = models.BooleanField(default=False, verbose_name=_('Set discount'))
    image = models.ImageField(default='discounts/product.png',
                              upload_to='discounts',
                              null=True,
                              blank=True,
                              verbose_name='discounts image')

    class Meta:
        verbose_name = _('product discount')
        verbose_name_plural = _('product discounts')
        db_table = 'product_discounts'

    def get_absolute_url(self) -> Callable:
        return reverse('discounts-polls:discount-detail', kwargs={'slug': self.slug,
                                                                  'pk': self.id})


class GroupDiscount(Discount):
    """
    Модель скидки на категорию товаров
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,
                               related_name='group_discounts',
                               verbose_name=_('Seller'))
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                         related_name=_('group_discounts'), verbose_name='Product categories',)

    class Meta:
        verbose_name = _('group discount')
        verbose_name_plural = _('group discounts')
        db_table = 'group_discounts'


class CartDiscount(Discount):
    """
    Модель скидки на корзину товаров
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,
                               related_name='cart_discounts',
                               verbose_name=_('Seller'))
    min_quantity_threshold = models.IntegerField(default=0, verbose_name=_('Min quantity threshold'))
    max_quantity_threshold = models.IntegerField(default=0, verbose_name=_('Max quantity threshold'))

    total_sum_min_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                  verbose_name=_('Total sum min threshold'))
    total_sum_max_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                  verbose_name=_('Total sum max threshold'))

    class Meta:
        verbose_name = _('cart discount')
        verbose_name_plural = _('cart discounts')
        db_table = 'cart_discounts'
