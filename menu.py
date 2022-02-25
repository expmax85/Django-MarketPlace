"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'python_django_team5.menu.CustomMenu'
"""
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.views import View

try:
    # we use django.urls import as version detection as it will fail on django 1.11 and thus we are safe to use
    # gettext_lazy instead of ugettext_lazy instead
    from django.urls import reverse
    from django.utils.translation import gettext_lazy as _
except ImportError:

    from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu


class HistoryMenuItem(items.MenuItem):
    title = 'History'

    def init_with_context(self, context):
        request = context['request']
        # we use sessions to store the visited pages stack
        history = request.session.get('history', [])
        for item in history:
            self.children.append(items.MenuItem(
                title=item['title'],
                url=item['url']
            ))
        # add the current page to the history
        history.insert(0, {
            'title': context['title'],
            'url': request.META['PATH_INFO']
        })
        if len(history) > 10:
            history = history[:10]
        request.session['history'] = history

class CustomMenu(Menu):
    """
    Custom Menu for python_django_team5 admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            # items.Bookmarks(),
            items.AppList(
                _('Applications'),
                exclude=('django.contrib.*', 'allauth.*', 'profiles_app.*'),
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*', 'allauth.*', 'profiles_app.*'),
                children=[items.MenuItem('Administration commands',
                               children=[
                                   items.MenuItem('Clear cache', url=reverse('admin-setup'))
                               ]
                               )],
            ),
        ]
        self.children.append(items.Bookmarks('My bookmarks'))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        super().init_with_context(context)


class ClearCache(View):

    def get(self, request):
        cache.clear()
        print('ok')
        message = _('Cache from app profiles_app was cleared.')
        # messages.add_message(request, messages.INFO, message, fail_silently=False)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


