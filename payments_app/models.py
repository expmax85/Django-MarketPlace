from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentRequest(models.Model):
    """
    Модель запроса оплаты
    """
    order = models.IntegerField(verbose_name=_('order number'))
    account = models.IntegerField(verbose_name=_('account number'))

    class Meta:
        verbose_name = _('payment request')
        verbose_name_plural = _('requests')
        db_table = 'payments'
