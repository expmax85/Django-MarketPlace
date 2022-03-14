from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views import View

from goods_app.services import random_product
from settings_app.config_project import SUCCESS_OPTIONS_ACTIVATE


class AdminView(PermissionRequiredMixin, View):
    permission_required = ('profiles_app.Content_manager', )

    def get(self, request):
        return render(request, 'admin/admin-setup.html')


@permission_required('profiles_app.Content_manager')
def clear_all_cache(request):
    cache.clear()
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, 'Cache was cleaned.')
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def change_limited_deal(request):
    random_product.manual_update_product()
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, 'The Limited deal product has changed successfully.')
    return redirect(request.META.get('HTTP_REFERER'))

@permission_required('profiles_app.Content_manager')
def update_expire(request):
    random_product.add_limited_deal_expire_days(3)
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, 'The Limited deal product has changed successfully.')
    return redirect(request.META.get('HTTP_REFERER'))
