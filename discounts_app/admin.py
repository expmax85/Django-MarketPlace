from django.contrib import admin
from discounts_app.models import (
    ProductDiscount,
    GroupDiscount,
    CartDiscount,
)


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('name', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(GroupDiscount)
class GroupDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('name', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CartDiscount)
class CartDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent',
                    'amount', 'fixed_price', 'valid_from', 'valid_to', 'is_active',
                    'min_quantity_threshold', 'max_quantity_threshold',
                    'total_sum_min_threshold', 'total_sum_max_threshold')
    list_filter = ('name', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'fixed_price', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}
