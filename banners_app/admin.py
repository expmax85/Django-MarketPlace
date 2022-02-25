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

    change_list_template = "admin/model_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('banner_cache/', self.clear_cache, name='clear_cache'), ]
        return custom_urls + urls

    def clear_cache(self, request):
        #Код очистки кэша
        self.message_user(request, _('Cache from applocation "Users" has cleared.'))
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
