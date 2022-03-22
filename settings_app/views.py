import datetime

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.shortcuts import render, redirect
from django.views import View

from goods_app.models import Product
from goods_app.services import random_product, get_limited_products
from settings_app.config_project import SUCCESS_OPTIONS_ACTIVATE, OPTIONS


User = get_user_model()


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
    random_product.update_product(queryset=get_limited_products(), manual=True)
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('The Limited product has changed successfully.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def update_expire(request):
    random_product.add_limited_deal_expire_days(days=OPTIONS['general__days_duration'])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('The Limited product days duration has changed.'))
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


@permission_required('profiles_app.Content_manager')
def clear_products_cache(request):
    cache.delete_many(['products:all_sp', 'categories:all_sp'])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_review_cache(request):
    all_reviews_cache = Product.objects.all().values('id')
    cache.delete_many([f'reviews:{item["id"]}' for item in list(all_reviews_cache)])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_detail_products_cache(request):
    list_products_id = list(Product.objects.all().values('id'))
    cache.delete_many([f'tags:{item["id"]}' for item in list_products_id])
    cache.delete_many([f'sellers:{item["id"]}' for item in list_products_id])
    cache.delete_many([f'specifications:{item["id"]}' for item in list_products_id])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_banner_cache(request):
    key = make_template_fragment_key('banners_block')
    cache.delete(key)
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_limited_products_cache(request):
    cache.delete('products:all')
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_users_cache(request):
    list_users_id = list(User.objects.all().values('id'))
    cache.delete_many([f'owner:{item["id"]}' for item in list_users_id])
    cache.delete_many([f'stores:{item["id"]}' for item in list_users_id])
    cache.delete_many([f'user_orders:{item["id"]}' for item in list_users_id])
    cache.delete_many([f'user_last_order:{item["id"]}' for item in list_users_id])
    cache.delete_many([f'viewed:{item["id"]}' for item in list_users_id])
    messages.add_message(request, SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))
