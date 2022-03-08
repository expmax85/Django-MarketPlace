"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'python_django_team5.menu.CustomMenu'
"""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    """
    Custom Menu for admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.AppList(
                _('Applications'),
                exclude=('django.contrib.*',
                         'allauth.*',
                         'profiles_app.*',
                         'dynamic_preferences.*',
                         'taggit.*',),
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',
                        'allauth.*',
                        'profiles_app.*',
                        'taggit.*',),
            ),
            items.AppList(_('Settings'),
                          models=('dynamic_preferences.*', ),
                          children=[
                               items.MenuItem(_('Settings'),
                                              url=reverse('admin-setup')),
                           ]
            ),
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        super().init_with_context(context)
