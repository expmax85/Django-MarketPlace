from django.contrib import admin

from banners_app.models import Banner


@admin.register(Banner)
class Banner(admin.ModelAdmin):
    list_display = ('title', 'discount')
    list_filter = ('title',)
    search_fields = ('title', 'discount')
