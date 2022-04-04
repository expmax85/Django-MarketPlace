from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from goods_app.models import ProductRequest
from stores_app.forms import AddRequestNewProductAdminForm
from stores_app.models import Seller, SellerProduct


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'seller', 'price', 'quantity')
    list_filter = ('product', 'seller', 'price', 'quantity')
    search_fields = ('product', 'seller', 'price', 'quantity')


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'user', 'store')
    list_filter = ('user', 'store', 'category')
    search_fields = ('name', 'store', 'category')
    readonly_fields = ('user', 'store', 'notes')
    form = AddRequestNewProductAdminForm

    actions = ['mark_published']

    def mark_published(self, request: HttpRequest, queryset: QuerySet) -> None:
        for item in queryset:
            item.is_published = True
            item.save(update_fields=['is_published'])

    mark_published.short_description = _('Publish')


# @admin.register(ProductImportFile)
# class ProductImportAdmin(admin.ModelAdmin):
#     list_display = ('file', )
#
#     def save_model(self, request, obj, form, change):
#
#         super(ProductImportAdmin, self).save_model(request, obj, form, change)
#         call_command('products_import', obj.file)
