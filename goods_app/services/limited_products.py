import random
import datetime as dt
from typing import Union, List, Dict

from django.core.cache import cache
from django.db.models import QuerySet, Model, Count, Min, Q, Sum

from stores_app.models import SellerProduct
from discounts_app.services import get_discounted_prices_for_seller_products
from goods_app.services.catalog import get_categories


class RandomProduct:
    """
    Class for controlling to update limited deal on main page. Takes 3 attributes:
    days_duration - number of days when product will update. Default=1
    time_update - time for product will update. Default its midnight.
    fallibility - its fallibility for js-code errors with countdown timer. Default=0

    Properties and setters:
    time_update,
    days_duration,
    end_time

    Allowed methods:
    update_product(queryset, manual),
    add_limited_deal_expire_days(days),
    get_context_data()

    """

    def __init__(self, time_update: dt.time = dt.time(hour=00, minute=00, second=00),
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
        """
        This method returns the time for the next product update as a string to pass this to javascript
        """
        return str((self.__end_time + self.__fallibility).strftime("%d.%m.%Y %H:%M"))

    @end_time.setter
    def end_time(self, datetime: dt.datetime) -> None:
        self.__end_time = datetime

    def add_limited_deal_expire_days(self, days: int) -> None:
        """
        Method for manually extending the next update time
        """
        self.__end_time += dt.timedelta(days=days)

    def update_product(self, queryset: QuerySet = None, manual: bool = False) -> Model:
        """
        Method for updating product if time is out. After updating, If manual is true, product updating
        is immediately without end time changes. Returns product
        """
        if manual:
            self.__product = get_limited_deal(queryset)
        elif dt.datetime.now() >= self.__end_time or self.__product == 'initial':
            self.__product = get_limited_deal(queryset)
            today = dt.date.today() + dt.timedelta(days=self.__days_duration)
            date = " ".join([str(today.strftime("%d.%m.%Y")), str(self.__time_update)[:-3]])
            self.__end_time = dt.datetime.strptime(date, "%d.%m.%Y %H:%M")
        return self.__product

    def get_context_data(self) -> Dict:
        """
        Method for fast making the context data
        """
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


def get_limited_products(count: int = -1) -> Union[QuerySet, bool]:
    """
    Function to get products for limited products block. Returns zip-iterator by count length with corteges
    (instance model, price with discount, type of discount)
    """
    products_cache_key = 'limited:all'
    queryset = cache.get(products_cache_key)
    if not queryset:
        queryset = SellerProduct.objects.select_related('seller', 'product',
                                                        'product__category',
                                                        'product__category__parent') \
                                        .filter(product__limited=True)
        if not list(queryset):
            return False
        cache.set(products_cache_key, queryset, 24 * 60 * 60)
    if count > 0:
        products = get_discounted_prices_for_seller_products(queryset[:count])
    else:
        products = get_discounted_prices_for_seller_products(queryset)
    return products


def get_hot_offers(count: int = 9) -> Union[QuerySet, None]:
    """
    Function to get products for hot offers block. Returns zip-iterator by count length with corteges
    (instance model, price with discount, type of discount)
    """
    products_cache_key = 'hot_offers:all'
    queryset = cache.get(products_cache_key)
    if not queryset:
        queryset = SellerProduct.objects.select_related('seller', 'product',
                                                        'product__category',
                                                        'product__category__parent') \
                                        .annotate(count=Count('product_discounts',
                                                              filter=Q(product_discounts__set_discount=False))) \
                                        .filter(count__gt=0).distinct()
        try:
            if len(list(queryset)) < count:
                queryset = random.choices(population=queryset, k=len(list(queryset)))
            else:
                queryset = random.choices(population=queryset, k=count)
        except IndexError:
            return None
        cache.set(products_cache_key, queryset, 24 * 60 * 60)
    products = get_discounted_prices_for_seller_products(queryset)
    return products


def get_limited_deal(products: QuerySet) -> Union[Model, None]:
    """
    Get one random product from products queryset. Return False if it does not exist. Return
    False if products is empty
    """
    try:
        return random.choice(list(products))
    except IndexError:
        return None


random_product = RandomProduct(fallibility=1)


def get_all_products(count: int) -> QuerySet:
    """
    Function to get all products. Returns zip-iterator by count length with corteges:
    (instance model, price with discount, type of discount) and with sort by order_by param
    """
    products_cache_key = 'products:all'
    queryset = cache.get(products_cache_key)
    if not queryset:
        queryset = SellerProduct.objects.select_related('seller', 'product',
                                                        'product__category',
                                                        'product__category__parent')\
                                        .annotate(buying=Count('order_products__quantity',
                                                               filter=Q(order_products__order__paid=True)))\
                                        .order_by('-buying')[:count]
        # queryset = order_products_by_quantity_selling(queryset)
        cache.set(products_cache_key, queryset, 24 * 60 * 60)
    products = get_discounted_prices_for_seller_products(queryset)
    return products


def get_random_categories() -> Union[List, None]:
    """
    Function to get 3 random categories, if it has at least 1 product. And the annotate for each category with
    minimal price from this category products. Returns QuerySet with 3 random elements or False if Queryset is empty
    """
    categories = get_categories()
    random_ctg_cache_key = 'random_categories:all'
    queryset = cache.get(random_ctg_cache_key)
    if not queryset:
        queryset = categories.annotate(count=Count('products__seller_products'),
                                       from_price=Min('products__seller_products__price')) \
                             .exclude(count=0)
        cache.set(random_ctg_cache_key, queryset, 24 * 60 * 60)
    try:
        random_categories = random.choices(population=list(queryset), k=3)
    except IndexError:
        return None
    return random_categories


def order_products_by_quantity_selling(queryset):
    temp_list = []
    for item in queryset:
        count = item.order_products.aggregate(Sum('quantity'))
        if count['quantity__sum'] is None:
            count['quantity__sum'] = 0
        temp_list.append(count['quantity__sum'])
    zp = zip(queryset, temp_list)
    zp = sorted(zp, key=lambda x: x[1], reverse=True)
    sort_list = [item[0] for item in zp]
    return sort_list
