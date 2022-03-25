from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from goods_app.models import ProductCategory, Product, ProductComment, Specifications, SpecificationsNames


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',), }


class SpecificationsAdmin(admin.TabularInline):
    model = Specifications


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'is_published', 'limited')
    list_filter = ('category', 'is_published', 'tags', 'limited')
    search_fields = ('name', 'code', 'category')
    prepopulated_fields = {'slug': ('name', 'code'),
                           'tags': ('category', )}

    inlines = [SpecificationsAdmin]

    actions = ['mark_published', 'mark_unpublished']

    def mark_published(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_published=True)

    def mark_unpublished(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_published=False)

    mark_published.short_description = _('Publish')
    mark_unpublished.short_description = _('Remove from publication')


@admin.register(ProductComment)
class ProductComment(admin.ModelAdmin):
    list_display = ('author', 'content', 'added')
    list_filter = ('author', 'added')
    search_fields = ('author', 'added')


@admin.register(Specifications)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('value', )


@admin.register(SpecificationsNames)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('name', )
