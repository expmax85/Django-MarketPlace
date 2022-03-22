from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from profiles_app.adminforms import GroupAdminForm, UserChangeForm, UserCreationForm
from profiles_app.models import UserRequest


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
    list_display = ('email', 'phone', 'is_staff', 'is_active')
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


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'seller')

    actions = ['make_sellers']

    def make_sellers(self, request, queryset):
        users = queryset.values('user_id')
        list_users = [item['user_id'] for item in list(users)]
        sellers = Group.objects.get(name='Sellers')
        all = User.objects.filter(id__in=list_users)
        for user in all:
            user.groups.add(sellers.id)
        queryset.delete()
