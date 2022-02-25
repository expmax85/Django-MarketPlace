from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.urls import path
from django.views import View

from profiles_app.adminforms import GroupAdminForm, UserChangeForm, UserCreationForm


User = get_user_model()
admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    """
    Use our custom form for controlling Groups
    """
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


class UserAdmin(BaseUserAdmin):
    """
    Setup the custom admin views fields and filters
    """
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'phone', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'address', 'avatar')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups',)

    change_list_template = "admin/model_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('profiles_cache/', self.clear_cache, name='clear_cache'), ]
        return custom_urls + urls

    def clear_cache(self, request):
        #Код очистки кэша
        self.message_user(request, _('Cache from applocation "Users" has cleared.'))
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)


