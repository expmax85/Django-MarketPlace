from django.contrib import admin
from orders_app.models import Order, OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer',)
    list_filter = ('customer',)
    search_fields = ('id', 'customer',)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'seller_product', 'final_price', 'quantity')
    list_filter = ('order', 'seller_product', 'final_price', 'quantity')
    search_fields = ('order', 'seller_product', 'final_price', 'quantity')
