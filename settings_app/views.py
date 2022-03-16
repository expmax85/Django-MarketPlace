import datetime

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views import View

from goods_app.services import random_product
from settings_app.config_project import SUCCESS_OPTIONS_ACTIVATE, OPTIONS


class AdminView(PermissionRequiredMixin, View):
    permission_required = ('profiles_app.Content_manager', )

    def get(self, request):
        return render(request, 'admin/admin-setup.html',)


@permission_required('profiles_app.Content_manager')
def clear_all_cache(request):
    cache.clear()
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def change_limited_deal(request):
    random_product.manual_update_product()
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('The Limited deal product has changed successfully.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def update_expire(request):
    random_product.add_limited_deal_expire_days(days=OPTIONS['general__days_duration'])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('The Limited deal product days duration has changed.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def set_expire(request):
    new_value = " ".join([request.GET.get('date'), request.GET.get('time')])
    dt = datetime.datetime.strptime(new_value, "%Y-%m-%d %H:%M")
    if dt > datetime.datetime.now():
        random_product.set_end_time(datetime=dt)
        messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('The time expire for limited deal was changed.'))
    else:
        messages.error(request, _('You need to choose datetime, later then now'))
    return redirect(request.META.get('HTTP_REFERER'))


def clear_products_cache(request):
    cache.delete_many(['all_products:all_sp', ])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


def clear_review_cache(request):
    # cache.delete_many(['reviews:{id}' for])
    pass