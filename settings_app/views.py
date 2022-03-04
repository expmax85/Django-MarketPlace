from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views import View


SUCCESS_CLEAR_CACHE = 200


class AdminView(PermissionRequiredMixin, View):
    permission_required = ('profiles_app.Content_manager', )

    def get(self, request):
        return render(request, 'admin/admin-setup.html')


@permission_required('profiles_app.Content_manager')
def clear_all_cache(request):
    cache.clear()
    messages.add_message(request, SUCCESS_CLEAR_CACHE, 'Cache was clean')
    return redirect(request.META.get('HTTP_REFERER'))
