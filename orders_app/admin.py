from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.translation import gettext_lazy as _

from orders_app.models import Order, OrderProduct
from stores_app.models import SellerProduct

#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'seller_product', 'final_price', 'quantity')
