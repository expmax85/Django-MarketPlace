from django.db import models


class Banner(models.Model):
    """
    Модель баннера
    """
    title = models.CharField(max_length=25, null=True)
    description = models.TextField(max_length=255, null=True)
    image = models.ImageField(null=True)
    #  link TODO нужно определить приаязываем к продукту или акции/скидке
