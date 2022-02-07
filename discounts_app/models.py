from django.db import models


class DiscountCategory(models.Model):
    """
    Модель категории скидки
    """
    name = models.CharField(max_length=25, null=True)
    slug = models.SlugField(null=True)
    description = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = 'discount categories'

    def __str__(self):
        return self.name


class Discount(models.Model):
    """
    Модель скидки
    """
    category = models.ForeignKey(DiscountCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=25, null=True)
    slug = models.SlugField(null=True)
    description = models.TextField(max_length=255, null=True)
    percent = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)

    def __str__(self):
        return self.name
