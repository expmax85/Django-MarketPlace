from django.contrib import admin
from discounts_app.models import DiscountCategory, Discount


@admin.register(DiscountCategory)
class DiscountCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'percent', 'amount', 'valid_from', 'valid_to')
    list_filter = ('name', 'category', 'percent', 'amount', 'valid_from', 'valid_to')
    search_fields = ('name', 'category', 'percent', 'amount', 'valid_from', 'valid_to')
    prepopulated_fields = {'slug': ('name', 'category')}
