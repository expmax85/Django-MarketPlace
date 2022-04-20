from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from goods_app.models import ProductRequest
from settings_app.forms import CheckImageForm
from stores_app.forms import AddRequestNewProductAdminForm
from stores_app.models import Seller, SellerProduct, ProductImportFile, ImportOrder


class SellerProductInLine(admin.TabularInline):
    model = SellerProduct


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    form = CheckImageForm
    list_display = ('get_icon', 'name', 'email', 'phone', 'owner')
    list_display_links = ('get_icon', 'name')
    list_filter = ('name', 'owner')
    readonly_fields = ('get_icon',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SellerProductInLine]

    def get_icon(self, obj):
        try:
            return mark_safe(f'<img src="{obj.icon.url}" width="60" height="50">')
        except ValueError:
            return mark_safe('<img src="" width="20" height="20">')

    get_icon.short_description = _('icon')


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller', 'price', 'quantity')
    list_filter = ('seller', )
    search_fields = ('product', )


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('get_image', 'name', 'is_published', 'user', 'store')
    list_display_links = ('get_image', 'name')
    list_filter = ('user', 'store', 'category')
    search_fields = ('name', 'store', 'category')
    readonly_fields = ('get_image', 'user', 'store', 'notes')
    form = AddRequestNewProductAdminForm

    actions = ['mark_published']

    def mark_published(self, request: HttpRequest, queryset: QuerySet) -> None:
        for item in queryset:
            item.is_published = True
            item.save(update_fields=['is_published'])

    mark_published.short_description = _('Publish')

    def get_image(self, obj):
        print(obj.image)
        try:
            return mark_safe(f'<img src="{obj.image.url}" width="60" height="60">')
        except ValueError:
            return mark_safe('<img src="" width="20" height="20">')

    get_image.short_description = _('image')
