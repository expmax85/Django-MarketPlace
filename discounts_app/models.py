from django.db import models
from django.utils.translation import gettext_lazy as _


class DiscountCategory(models.Model):
    """
    Discount category model
    """
    name = models.CharField(verbose_name=_("title discount category"), max_length=25, null=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name=_("description"), max_length=255, null=True)

    class Meta:
        verbose_name = _('discount category')
        verbose_name_plural = _('discount categories')
        db_table = 'category_discount'

    def __str__(self):
        return self.name


class Discount(models.Model):
    """
    Discount model
    """
    category = models.ForeignKey(DiscountCategory, on_delete=models.CASCADE,
                                 related_name='products', verbose_name=_('category'))
    name = models.CharField(verbose_name=_("title discount"), max_length=25, null=True)
    slug = models.SlugField()
    description = models.TextField(verbose_name=_("description"), max_length=255, null=True, blank=True)
    percent = models.FloatField(verbose_name=_("percent"), null=True, blank=True)
    amount = models.FloatField(verbose_name=_("amount"), null=True, blank=True)
    valid_from = models.DateTimeField(verbose_name=_("valid_from"), null=True)
    valid_to = models.DateTimeField(verbose_name=_("valid_to"), null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('discount')
        verbose_name_plural = _('discounts')
        db_table = 'discount'
