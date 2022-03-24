import random
import datetime as dt
from typing import Union, List

from django.core.cache import cache
from django.db.models import QuerySet, Model, Count, Min, Prefetch

from discounts_app.models import ProductDiscount
from stores_app.models import SellerProduct
from discounts_app.services import get_discounted_prices_for_seller_products
from goods_app.services.catalog import get_categories


class RandomProduct:

    def __init__(self, time_update: dt.time = dt.time(hour=00, minute=45, second=00),
                 days_duration: int = 1, fallibility: int = 0) -> None:
        self.__days_duration = days_duration
        self.__time_update = time_update
        self.__fallibility = dt.timedelta(days=fallibility)
        self.__product = 'initial'
        base_day = dt.date.today() - dt.timedelta(days=1)
        date = " ".join([str(base_day.strftime("%d.%m.%Y")), str(self.time_update)[:-3]])
        self.__end_time = dt.datetime.strptime(date, "%d.%m.%Y %H:%M")

    @property
    def time_update(self) -> dt.time:
        return self.__time_update

    @time_update.setter
    def time_update(self, value: dt.time) -> None:
        self.__time_update = value

    @property
    def days_duration(self) -> int:
        return self.__days_duration

    @days_duration.setter
    def days_duration(self, value: int) -> None:
        self.__days_duration = value

    @property
    def end_time(self) -> str:
        return str((self.__end_time + self.__fallibility).strftime("%d.%m.%Y %H:%M"))

    @end_time.setter
    def end_time(self, datetime: dt.datetime) -> None:
        self.__end_time = datetime

    def add_limited_deal_expire_days(self, days: int) -> None:
        self.__end_time += dt.timedelta(days=days)

    def update_product(self, queryset=None, manual=False) -> Model:
        if manual:
            self.__product = get_limited_deal(queryset)
            return self.__product

        if dt.datetime.now() >= self.__end_time or self.__product == 'initial':
            self.__product = get_limited_deal(queryset)
            today = dt.date.today() + dt.timedelta(days=self.__days_duration)
            date = " ".join([str(today.strftime("%d.%m.%Y")), str(self.__time_update)[:-3]])
            self.__end_time = dt.datetime.strptime(date, "%d.%m.%Y %H:%M")
        return self.__product

    def get_context_data(self):
        if self.__product and self.__product != 'initial':
            return {
                'special_product': self.__product[0],
                'special_discount_price': self.__product[1],
                'special_discount': self.__product[2],
                'update_time': self.end_time
            }
        return {
                'special_product': False,
                'special_discount_price': False,
                'special_discount': None,
                'update_time': None
            }


def get_limited_products(count: int) -> QuerySet:
    products_cache_key = 'limited:{}'.format('all')
    queryset = cache.get(products_cache_key)
    if not queryset:
        queryset = SellerProduct.objects.select_related('seller', 'product', 'product__category')\
                                        .prefetch_related(Prefetch('product_discounts',
                                            queryset=ProductDiscount.objects.filter(is_active=True,
                                                                                    type_of_discount__in=('f', 'p'))))\
                                        .filter(product__limited=True)[:count]
        cache.set(products_cache_key, queryset, 60 * 60)
    products = get_discounted_prices_for_seller_products(queryset)
    return products


def get_hot_offers(count: int=9):
    products_cache_key = 'hot_offers:{}'.format('all')
    queryset = cache.get(products_cache_key)
    if not queryset:
        queryset = SellerProduct.objects.select_related('seller', 'product', 'product__category') \
                                        .prefetch_related(Prefetch('product_discounts',
                                            queryset=ProductDiscount.objects.prefetch_related('seller_products')
                                                                            .filter(is_active=True,
                                                                                    type_of_discount__in=('f', 'p'))))\
                                        .annotate(count=Count('product_discounts'))\
                                        .filter(count__gt=0)
        if len(list(queryset)) < count:
            queryset = random.choices(population=queryset, k=len(list(queryset)))
        else:
            queryset = random.choices(population=queryset, k=count)
        cache.set(products_cache_key, queryset, 60 * 60)
    products = get_discounted_prices_for_seller_products(queryset)
    return products


def get_limited_deal(products: QuerySet) -> Union[Model, bool]:
    try:
        return random.choice(list(products))
    except IndexError:
        return False


random_product = RandomProduct(fallibility=1)


def get_all_products(order_by: str, count: int) -> QuerySet:
    products_cache_key = 'products:{}'.format('all_sp')
    queryset = cache.get(products_cache_key)
    if not queryset:
        queryset = SellerProduct.objects.select_related('seller', 'product', 'product__category') \
                                        .prefetch_related(Prefetch('product_discounts',
                                            queryset=ProductDiscount.objects.filter(is_active=True,
                                                                                    type_of_discount__in=('f', 'p'))))\
                                        .all().order_by(order_by)[:count]
        cache.set(products_cache_key, queryset, 60 * 60)
    products = get_discounted_prices_for_seller_products(queryset)
    return products


def get_random_categories() -> Union[List, bool]:
    categories = get_categories()
    random_categories = categories.annotate(count=Count('products__seller_products'),
                                            from_price=Min('products__seller_products__price'))\
                                  .exclude(count=0)
    try:
        random_categories = random.choices(population=list(random_categories), k=3)
    except IndexError:
        return False
    return random_categories
