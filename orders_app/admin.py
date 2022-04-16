from django.contrib import admin
from orders_app.models import Order, OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'phone', 'email', 'payment_method',
                    'in_order', 'paid', 'ordered', 'delivery_cost', 'final_total')

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'seller_product', 'final_price', 'quantity')

