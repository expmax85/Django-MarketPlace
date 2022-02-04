from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'email', 'phone', 'city',)
    list_filter = ('first_name', 'city',)
