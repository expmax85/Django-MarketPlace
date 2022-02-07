from django.db import models
from django.utils.translation import gettext_lazy as _
from discounts_app.models import Discount


class Banner(models.Model):
    """
    Модель баннера
    """
    discount = models.OneToOneField(Discount, on_delete=models.CASCADE,
                                    null=True,
                                    related_name='discount_banner',
                                    verbose_name=_('discount_banner'))
    title = models.CharField(max_length=25, null=True, verbose_name=_('banner_title'))
    description = models.TextField(max_length=255, null=True, verbose_name=_('banner_description'))
    image = models.ImageField(upload_to='static/assets/img/content/home/banners',
                              null=True,
                              blank=True,
                              verbose_name=_('banner_image'))

    class Meta:
        db_table = 'banners'

    def __str__(self):
        return self.title
