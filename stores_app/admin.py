from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.translation import gettext_lazy as _

from stores_app.models import Seller, SellerProduct


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    change_list_template = "admin/model_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('stores_cache/', self.clear_cache, name='clear_cache'), ]
        return custom_urls + urls

    def clear_cache(self, request):
        #Код очистки кэша
        self.message_user(request, _('Cache from application "Users" has cleared.'))
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'seller', 'price', 'discount', 'price_after_discount', 'quantity')
    list_filter = ('product', 'seller', 'price', 'discount', 'price_after_discount', 'quantity')
    search_fields = ('product', 'seller', 'price', 'discount', 'price_after_discount', 'quantity')
