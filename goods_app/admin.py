from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from goods_app.models import ProductCategory, Product, ProductComment


# @admin.register(ProductCategory)
# class ProductCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug')
#     list_filter = ('name',)
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}


class ProductCategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = ProductCategory.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = ProductCategory.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


admin.site.register(ProductCategory, ProductCategoryAdmin2)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', )
    list_filter = ('name', 'code', 'category')
    search_fields = ('name', 'code', 'category')
    prepopulated_fields = {'slug': ('name', 'category')}


@admin.register(ProductComment)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'added', )
    list_filter = ('author', 'added')
    search_fields = ('author', 'added')
