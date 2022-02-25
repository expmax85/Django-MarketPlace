from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.translation import gettext_lazy as _

from orders_app.models import Order, OrderProduct
from stores_app.models import SellerProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    change_list_template = "admin/model_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('orders_cache/', self.clear_cache, name='clear_cache'), ]
        return custom_urls + urls

    def clear_cache(self, request):
        #Код очистки кэша
        self.message_user(request, _(f'Cache from application {self.model._meta.verbose_plural_name} has cleared.'))
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
#
#
# @admin.register(OrderProduct)
# class OrderProductAdmin(admin.ModelAdmin):
#     list_display = ('order', 'seller_product', 'final_price', 'quantity')
#     list_filter = ('order', 'seller_product', 'final_price', 'quantity')
#     search_fields = ('order', 'seller_product', 'final_price', 'quantity')

