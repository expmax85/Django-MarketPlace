from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.translation import gettext_lazy as _

from banners_app.models import Banner


@admin.register(Banner)
class Banner(admin.ModelAdmin):
    list_display = ('id', 'title', 'discount')
    list_filter = ('title',)
    search_fields = ('title', 'discount')
