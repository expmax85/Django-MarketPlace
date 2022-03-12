from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _


# class DiscountCategory(models.Model):
#     """
#     Discount category model
#     """
#     name = models.CharField(verbose_name=_("title discount category"),
#                             max_length=25, null=True)
#     slug = models.SlugField(unique=True)
#     description = models.TextField(verbose_name=_("description"),
#                                    max_length=255, null=True)
#
#     class Meta:
#         verbose_name = _('discount category')
#         verbose_name_plural = _('discount categories')
#         db_table = 'category_discount'
#
#     def __str__(self):
#         return self.name
from goods_app.models import ProductCategory
from stores_app.models import Seller, SellerProduct

TYPE_CHOICES = [
        ('p', _('Per cent')),
        ('f', _('Fixed amount')),
    ]

PRIORITY_CHOICES = [
        ('1', _('Low')),
        ('2', _('Medium')),
        ('3', _('High')),
    ]


class Discount(models.Model):
    """
    Abstract discount model
    """
    name = models.CharField(verbose_name=_("title discount"), max_length=25, null=True)
    slug = models.SlugField()
    description = models.TextField(verbose_name=_("description"), max_length=255,
                                   null=True, blank=True)
    type_of_discount = models.CharField(max_length=1, choices=TYPE_CHOICES,
                                        default='p', verbose_name=_('discount type'))
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES,
                                default='1', verbose_name=_('priority'))
    percent = models.FloatField(verbose_name=_("percent"),
                                null=True, blank=True,
                                validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                default=0)
    amount = models.FloatField(verbose_name=_("amount"),
                               null=True, blank=True,
                               validators=[MinValueValidator(0.0)],
                               default=0)
    valid_from = models.DateTimeField(verbose_name=_("valid_from"), null=True, blank=True)
    valid_to = models.DateTimeField(verbose_name=_("valid_to"), null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

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
    ProductDiscount model
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,
                               related_name='product_discounts',
                               verbose_name=_('seller'))
    seller_products = models.ManyToManyField(SellerProduct, related_name='product_discounts',
                                             verbose_name=_('seller_product'))

    class Meta:
        verbose_name = _('product_discount')
        verbose_name_plural = _('product_discounts')
        db_table = 'product_discounts'


class GroupDiscount(Discount):
    """
    GroupDiscount model
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,
                               related_name='group_discounts',
                               verbose_name=_('seller'))
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                         related_name=_('group_discounts'), verbose_name='products',)

    class Meta:
        verbose_name = _('group_discount')
        verbose_name_plural = _('group_discounts')
        db_table = 'group_discounts'


class CartDiscount(Discount):
    """
    CartDiscount model
    """
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,
                               related_name='cart_discounts',
                               verbose_name=_('seller'))
    min_quantity_threshold = models.IntegerField(default=0, verbose_name=_('min_quantity_threshold'))
    max_quantity_threshold = models.IntegerField(default=0, verbose_name=_('max_quantity_threshold'))

    total_sum_min_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                  verbose_name=_('total_sum_min_threshold'))
    total_sum_max_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                  verbose_name=_('total_sum_max_threshold'))

    class Meta:
        verbose_name = _('cart_discount')
        verbose_name_plural = _('cart_discounts')
        db_table = 'cart_discounts'
