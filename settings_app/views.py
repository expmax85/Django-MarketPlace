import datetime
from typing import Callable

from django.contrib import messages
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.shortcuts import render, redirect
from django.views import View
from dynamic_preferences.registries import global_preferences_registry

from django.conf import settings
from goods_app.services.limited_products import random_product, get_limited_products
from goods_app.models import Product
from stores_app.models import Seller

User = get_user_model()


class AdminView(PermissionRequiredMixin, View):
    """
    Страница настроек сайта в админ-панели

    ::Страница: Настройки
    """
    permission_required = ('profiles_app.Content_manager',)

    def get(self, request: HttpRequest) -> Callable:
        return render(request, 'admin/admin-setup.html', )


@permission_required('profiles_app.Content_manager')
def clear_all_cache(request: HttpRequest) -> Callable:
    """
    Очистка всего кеша сайта

    ::Страница: Настройки
    """
    cache.clear()
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def change_limited_deal(request: HttpRequest) -> Callable:
    """
    Представление ручного изменения товара из блока "Ограниченный тираж"

    ::Страница: Настройки
    """
    OPTIONS = global_preferences_registry.manager().by_name()
    limited_products = get_limited_products(count=OPTIONS['count_limited_products'])
    random_product.update_product(queryset=limited_products, manual=True)
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('The Limited product has changed successfully.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def update_expire(request: HttpRequest) -> Callable:
    """
    Представление для продления времени следующего обновления товара из "Ограниченного тиража"

    ::Страница: Настройки
    """
    OPTIONS = global_preferences_registry.manager().by_name()
    random_product.add_limited_deal_expire_days(days=OPTIONS['days_duration'])
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE,
                         _('The Limited product days duration has changed.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def set_expire(request: HttpRequest) -> Callable:
    """
    Представление для ручного ввода даты и времени следующего обновления товара из "Ограниченного тиража"

    ::Страница: Настройки
    """
    new_value = " ".join([request.GET.get('date'), request.GET.get('time')])
    dt = datetime.datetime.strptime(new_value, "%Y-%m-%d %H:%M")
    if dt > datetime.datetime.now():
        random_product.end_time = dt
        messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE,
                             _('The time expire for limited deal was changed.'))
    else:
        messages.error(request, _('You need to choose datetime, later then now'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_catalog_cache(request: HttpRequest) -> Callable:
    """
    Очистка кэша продуктов и категорий каталога

    ::Страница: Настройки
    """
    cache.delete_many(['products:all',
                       'categories:all',
                       'limited:all',
                       'hot_offers:all',
                       'stores:all',
                       'random_categories:all'])
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_review_cache(request: HttpRequest) -> Callable:
    """
    Очистка кеша отзывов о товарах

    ::Страница: Настройки
    """
    all_reviews_cache = Product.objects.all().values('id')
    cache.delete_many([f'reviews:{item["id"]}' for item in list(all_reviews_cache)])
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_detail_products_cache(request: HttpRequest) -> Callable:
    """
    Очистка кеша детальных страниц товаров (кроме отзывов)

    ::Страница: Настройки
    """
    list_products_id = list(Product.objects.all().values('id'))
    cache.delete_many([f'tags:{item["id"]}' for item in list_products_id])
    cache.delete_many([f'sellers:{item["id"]}' for item in list_products_id])
    cache.delete_many([f'specifications:{item["id"]}' for item in list_products_id])
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_banner_cache(request: HttpRequest) -> Callable:
    """
    Очистка кеша баннеров

    ::Страница: Настройки
    """
    key = make_template_fragment_key('banners_block')
    cache.delete(key)
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_sellers_cache(request: HttpRequest) -> Callable:
    """
    Очистка кеша продавцов

    ::Страница: Настройки
    """
    list_owner = list(set([item['owner_id'] for item in Seller.objects.all().values('owner_id')]))
    cache.delete_many([f'owner_sp:{i}' for i in list_owner])
    cache.delete_many([f'stores:{i}' for i in list_owner])
    cache.delete_many([f'owner_product_discounts:{i}' for i in list_owner])
    cache.delete_many([f'owner_group_discounts:{i}' for i in list_owner])
    cache.delete_many([f'owner_card_discounts:{i}' for i in list_owner])
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Content_manager')
def clear_users_cache(request: HttpRequest) -> Callable:
    """
    Очистка кеша пользователей

    ::Страница: Настройки
    """
    list_users_id = list(User.objects.all().values('id'))
    cache.delete_many([f'user_orders:{item["id"]}' for item in list_users_id])
    cache.delete_many([f'user_last_order:{item["id"]}' for item in list_users_id])
    cache.delete_many([f'viewed:{item["id"]}' for item in list_users_id])
    messages.add_message(request, settings.SUCCESS_OPTIONS_ACTIVATE, _('Cache was cleaned.'))
    return redirect(request.META.get('HTTP_REFERER'))
