from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.translation import gettext_lazy as _

from goods_app.models import ProductCategory, Product, ProductComment, Specifications, SpecificationsNames


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    change_list_template = "admin/model_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('stores_cache/', self.clear_cache, name='clear_cache'), ]
        return custom_urls + urls

    def clear_cache(self, request):
        #Код очистки кэша
        self.message_user(request, _('Cache from applocation "Users" has cleared.'))
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class SpecificationsAdmin(admin.TabularInline):
    model = Specifications


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category')
    list_filter = ('name', 'code', 'category')
    search_fields = ('name', 'code', 'category')
    prepopulated_fields = {'slug': ('name', 'category')}

    inlines = [SpecificationsAdmin]


@admin.register(ProductComment)
class ProductComment(admin.ModelAdmin):
    list_display = ('author', 'content', 'added')
    list_filter = ('author', 'added')
    search_fields = ('author', 'added')


@admin.register(Specifications)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('value',)


@admin.register(SpecificationsNames)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
