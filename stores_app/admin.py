from django.contrib import admin
from stores_app.models import Seller, SellerProduct


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    list_filter = ('name',)
    search_fields = ('name',)
    # prepopulated_fields = {'slug': ('id', 'name')}


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'seller', 'price', 'discount', 'price_after_discount', 'quantity')
    list_filter = ('product', 'seller', 'price', 'discount', 'price_after_discount', 'quantity')
    search_fields = ('product', 'seller', 'price', 'discount', 'price_after_discount', 'quantity')
