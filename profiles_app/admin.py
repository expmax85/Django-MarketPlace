from django.contrib import admin
from profiles_app.models import Customer


@admin.register(Customer)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'city',)
    list_filter = ('name', 'city',)
    search_fields = ('name', 'phone', 'city',)
