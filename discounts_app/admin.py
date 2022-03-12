from django.contrib import admin

from discounts_app.models import (
    # DiscountCategory,
    # Discount,
    ProductDiscount,
    GroupDiscount,
    CartDiscount,
)


# @admin.register(DiscountCategory)
# class DiscountCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     list_filter = ('name',)
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}


# @admin.register(Discount)
# class DiscountAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'percent', 'amount', 'valid_from', 'valid_to')
#     list_filter = ('name', 'category', 'percent', 'amount', 'valid_from', 'valid_to')
#     search_fields = ('name', 'category', 'percent', 'amount', 'valid_from', 'valid_to')
#     prepopulated_fields = {'slug': ('name', 'category')}
from stores_app.models import SellerProduct


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_discount', 'priority', 'percent', 'amount', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    search_fields = ('name', 'percent', 'amount', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name',)}

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     print(db_field.name)
    #     if db_field.name == "seller_products":
    #         kwargs["queryset"] = SellerProduct.objects.filter(seller=request.user)
    #     return super(ProductDiscountAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


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
