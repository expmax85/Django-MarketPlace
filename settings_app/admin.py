from django.contrib import admin
from dynamic_preferences.admin import GlobalPreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel


admin.AdminSite.site_title = 'MEGANO'
admin.AdminSite.index_title = 'Administration'
admin.site.unregister(GlobalPreferenceModel)


class PreferenceAdmin(GlobalPreferenceAdmin):
    list_display = ('verbose_name',  'help_text', 'raw_value', 'default_value')
    fields = ('raw_value', 'default_value', 'help_text', 'name')
    readonly_fields = ('default_value', 'help_text', 'name')
    search_fields = ['verbose_name', 'name', 'raw_value']
    list_filter = ()

    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(GlobalPreferenceModel, PreferenceAdmin)

