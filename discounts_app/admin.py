from django.contrib import admin
from django.forms import ModelChoiceField
from discounts_app.models import (
    ProductDiscount,
    GroupDiscount,
    CartDiscount,
)
from stores_app.models import Seller


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent', 'amount', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'seller':
    #         return ModelChoiceField(Seller.objects.filter(owner=request.user))
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(GroupDiscount)
class GroupDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent', 'amount', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CartDiscount)
class CartDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent',
                    'amount', 'valid_from', 'valid_to', 'is_active',
                    'min_quantity_threshold', 'max_quantity_threshold',
                    'total_sum_min_threshold', 'total_sum_max_threshold')
    list_filter = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}
