from typing import Callable

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

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
    list_display = ('get_avatar', 'email', 'phone', 'is_staff', 'is_active')
    list_display_links = ('get_avatar', 'email', )
    list_filter = ('is_staff', 'city', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'address', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'groups')}),
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

    def get_avatar(self, obj) -> Callable:
        try:
            return mark_safe(f'<img src="{obj.avatar.url}" width="50" height="60">')
        except ValueError:
            return mark_safe('<img src="" width="20" height="20">')

    get_avatar.short_description = _('avatar')


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
