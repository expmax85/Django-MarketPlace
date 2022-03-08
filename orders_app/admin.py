from django.contrib import admin
from orders_app.models import Order, OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'phone', 'email', 'payment_method',
                    'in_order', 'paid', 'ordered')


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'seller_product', 'final_price', 'quantity')
