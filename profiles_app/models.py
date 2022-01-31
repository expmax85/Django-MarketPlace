from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    """
    Модель покупателя
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=25, null=True)
    slug = models.SlugField(null=True)
    image = models.ImageField(null=True)
    phone = models.CharField(max_length=255, null=True)
    address = models.TextField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
