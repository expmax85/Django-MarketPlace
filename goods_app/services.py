import random
import datetime as dt
from typing import List, Dict, Tuple, Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet, Model

from goods_app.models import ProductCategory, ProductComment, Product
from settings_app.config_project import OPTIONS
from stores_app.models import SellerProduct


class RandomProduct:

    def __init__(self, queryset: QuerySet, time_update: dt.time = dt.time(hour=00, minute=45, second=00),
                 days_duration: int = 1, fallibility: int = 0) -> None:
        if not isinstance(queryset, QuerySet):
            raise ValueError('RandomItem must receive Queryset')
        self.queryset = queryset
        self.days_duration = days_duration
        self.time_update = time_update
        self.fallibility = dt.timedelta(days=fallibility)
        self.product = get_limited_deal(list(self.queryset))
        today = dt.date.today() + dt.timedelta(days=self.days_duration)
        date = " ".join([str(today.strftime("%d.%m.%Y")), str(self.time_update)[:-3]])
        self.end_time = dt.datetime.strptime(date, "%d.%m.%Y %H:%M")

    def update_product(self) -> Model:
        if dt.datetime.now() >= self.end_time:
            self.product = get_limited_deal(list(self.queryset))
            today = dt.date.today() + dt.timedelta(days=self.days_duration)
            date = " ".join([str(today.strftime("%d.%m.%Y")), str(self.time_update)[:-3]])
            self.end_time += dt.datetime.strptime(date, "%d.%m.%Y %H:%M")
        return self.product

    def set_time_update(self, time_update: dt.time) -> None:
        self.time_update = time_update

    def set_days_duration(self, days_duration: int) -> None:
        self.days_duration = days_duration

    def set_end_time(self, datetime: dt.datetime):
        self.end_time = datetime

    @property
    def get_end_time(self) -> str:
        return str((self.end_time + self.fallibility).strftime("%d.%m.%Y %H:%M"))

    def manual_update_product(self):
        self.product = get_limited_deal(list(self.queryset))

    def add_limited_deal_expire_days(self, days):
        self.end_time += dt.timedelta(days=days)


def get_seller_products() -> QuerySet:
    products_cache_key = 'all_products:{}'.format('all_sp')
    products = cache.get(products_cache_key)
    if not products:
        products = SellerProduct.objects.select_related('seller', 'product', 'discount', 'product__category').all()
        cache.set(products_cache_key, products, 60 * 60)
    return products


def get_limited_deal(list_products: List) -> Model:
    return random.choice(list(list_products))


# random_product = RandomProduct(queryset=get_seller_products(), fallibility=1)


class CurrentProduct:

    def __init__(self, **kwargs) -> None:
        if 'slug' in kwargs:
            self.product = Product.objects.get(slug=kwargs['slug'])
        elif 'instance' in kwargs:
            self.product = kwargs['instance']
        else:
            raise ValueError

    @property
    def get_product(self) -> Product:
        return self.product

    @property
    def get_sellers(self) -> QuerySet:
        return SellerProduct.objects.select_related('seller', 'product', 'discount', 'product__category') \
            .filter(product=self.product) \
            .order_by('price_after_discount')

    @property
    def get_best_offer(self) -> QuerySet:
        return self.get_sellers.first()

    @property
    def get_specifications(self) -> QuerySet:
        specifications_cache_key = 'specifications:{}'.format(self.product.id)
        specifications = cache.get(specifications_cache_key)
        if not specifications:
            specifications = self.product.specifications.all()
            cache.set(specifications_cache_key, specifications, 24 * 60 * 60)
        return specifications

    @property
    def get_tags(self) -> QuerySet:
        return self.product.tags.all()

    @property
    def get_reviews(self) -> QuerySet:
        reviews_cache_key = 'reviews:{}'.format(self.product.id)
        reviews = cache.get(reviews_cache_key)
        if not reviews:
            reviews = self.product.product_comments.all()
            cache.set(reviews_cache_key, reviews, 24 * 60 * 60)
        return reviews

    def get_review_page(self, queryset: QuerySet, page: int) -> Dict:
        reviews_count = queryset.count()
        reviews = queryset.values('author', 'content', 'added')
        paginator = Paginator(reviews, per_page=OPTIONS['general__review_size_page'])
        page_obj = paginator.get_page(page)
        json_dict = {
            'comments': list(page_obj.object_list),
            'has_previous': None if page_obj.has_previous() is False
            else "previous",
            'previous_page_number': page_obj.number - 1,
            'num_pages': page_obj.paginator.num_pages,
            'number': page_obj.number,
            'has_next': None if page_obj.has_next() is False
            else "next",
            'next_page_number': page_obj.number + 1,
            'empty_pages': None if page_obj.paginator.num_pages < 2
            else "not_empty",
            'reviews_count': reviews_count
        }
        return json_dict

    def calculate_product_rating(self) -> None:
        rating = ProductComment.objects.only('rating') \
            .filter(product_id=self.product.id) \
            .aggregate(Avg('rating'))['rating__avg']
        if rating:
            self.product.rating = round(float(rating), 0)
            self.product.save(update_fields=['rating'])

    def get_context_data(self, *args) -> Dict:
        context = dict()
        for arg in args:
            try:
                context[str(arg)] = getattr(self, ''.join(['get_', str(arg)]))
            except AttributeError as err:
                raise AttributeError(err)
        return context


@receiver(post_save, sender=ProductComment)
def comment_post_save_handler(sender, **kwargs):
    if kwargs['created']:
        product_id = kwargs['instance'].product_id
        cache.delete('reviews:{}'.format(product_id))


def context_pagination(request, queryset: QuerySet, size_page: int = 3) -> Paginator:
    """
    Функция для создания пагинации
    :return: Paginator
    """
    paginator = Paginator(queryset, size_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


class CatalogByCategoriesMixin:
    """
    класс-миксин для классбэйсд вью, для всех необходимых действий с каталогом
    """

    @classmethod
    def simple_sort(cls, some_list: List, sort_type: str) -> Tuple:
        """
        метод сортирует входящую последовательность в соответствии с заданным типом м направлением сортировки
        :param some_list: входящая последовательность для сортировки
        :param sort_type: тип сортировки - указывает на поле, по которому будет осуществляться сортировка и направление(возрастание/убывание)
        :return:    some_list - отсортированный массив
                    next_state - следующее состояние типа сортировки(т.к. направление сортировки меняется при повторном нажатии)
        """
        next_state = ''

        if sort_type == 'name_inc':
            next_state = 'name_dec'
            some_list = cls.sort_by_name(some_list, False)

        if sort_type == 'name_dec':
            next_state = 'name_inc'
            some_list = cls.sort_by_name(some_list, True)

        if sort_type == 'price_inc':
            next_state = 'price_dec'
            some_list = cls.sort_by_price(some_list, False)

        if sort_type == 'price_dec':
            next_state = 'price_inc'
            some_list = cls.sort_by_price(some_list, True)

        if sort_type == 'comment_inc':
            next_state = 'comment_dec'
            some_list = cls.sort_by_amount_of_comments(some_list, False)

        if sort_type == 'comment_dec':
            next_state = 'comment_inc'
            some_list = cls.sort_by_amount_of_comments(some_list, True)

        if sort_type == 'pop_inc':
            next_state = 'pop_dec'
            some_list = []

        if sort_type == 'pop_dec':
            next_state = 'pop_inc'
            some_list = []

        return some_list, next_state

    @classmethod
    def get_data_without_filters(cls, slug: str) -> Tuple[List, Any, set, List]:
        """
        метод для получения всех необходимых данных для отрисовки каталога при условии отсутствия фильтров
        :param slug: уникальных слаг категории товаров

        :return:    items_for_catalog - список товаров из магазина для отрисовки в каталоге
                    category - категория товаров
                    sellers - список уникальных продавцов
                    tags - список первых 6-ти самых популярных тэгов
        """

        category = ProductCategory.objects.prefetch_related(
            'products',
            'products__seller_products',
            'products__seller_products__seller',
            'products__tags',
        ).get(slug=slug)

        products_set = category.products.all()

        sellers = []
        items_for_catalog = []
        tags = []

        for elem in products_set:
            items_for_catalog.extend(elem.seller_products.all())
            tags.extend(elem.tags.all())
            for el in elem.seller_products.all():
                sellers.append(el.seller)

        tags = tags[:6]
        return items_for_catalog, category, set(sellers), tags

    @classmethod
    def get_data_with_filters(cls, slug: str, filter_data: Dict) -> Tuple[List, Any, set]:
        """
        метод для получения всех необходимых данных для отрисовки каталога с фильтрами
        :param slug: уникальных слаг категории товаров
        :param filter_data: словарь со значениями фильтров для отображения карточек товаров в магазинах

        :return:    items_for_catalog - список товаров из магазина для отрисовки в каталоге
                    category - категория товаров
                    sellers - список уникальных продавцов
        """
        category = ProductCategory.objects.prefetch_related(
            'products',
            'products__seller_products',
            'products__seller_products__seller',
            'products__tags',
        ).get(slug=slug)

        products_set = category.products.all()

        sellers = []

        for elem in products_set:
            for el in elem.seller_products.all():
                sellers.append(el.seller)

        items_for_catalog = SellerProduct.objects.select_related('product', 'seller', 'discount') \
            .prefetch_related('product__category', 'product__tags') \
            .filter(
            seller__name__icontains=filter_data['f_select'],
            product__tags__name__icontains=filter_data['tag'],
            product__name__icontains=filter_data['f_title'],
            product__category__name__icontains=category,
            price_after_discount__range=(int(filter_data['f_price'][0]), int(filter_data['f_price'][1])),
            quantity__gte=filter_data['in_stock']
        ).annotate(Count('product__product_comments'))

        return items_for_catalog, category, set(sellers)

    @classmethod
    def sort_by_name(cls, some_list: List, direction: bool) -> List:
        """
        метод сортировки товаров в магазинах по наименованию
        :param some_list: исходный список товаров
        :param direction: направление сорировки; true - по возрастанию, false - по убыванию
        :return: отсортированный по наименованию список
        """
        return sorted(some_list, key=lambda x: x.product.name, reverse=direction)

    @classmethod
    def sort_by_price(cls, some_list: List, direction: bool) -> List:
        """
        метод сортировки товаров в магазинах по стоимости
        :param some_list: исходный список товаров
        :param direction: направление сорировки; true - по возрастанию, false - по убыванию
        :return: отсортированный по стоимости список
        """
        return sorted(some_list, key=lambda x: x.price_after_discount if x.price_after_discount else x.price,
                      reverse=direction)

    @classmethod
    def sort_by_amount_of_comments(cls, some_list: List, direction: bool) -> List:
        """
        метод сортировки товаров в магазинах по количеству комментариев
        :param some_list: исходный список товаров
        :param direction: направление сорировки; true - по возрастанию, false - по убыванию
        :return: отсортированный по количеству комментариев список
        """
        return sorted(some_list, key=lambda x: len(x.product.product_comments.all()), reverse=direction)

    @classmethod
    def get_min_price(cls, some_list: List) -> int or float:
        """
        метод для получения минимальной стоимости товара из списка товаров
        :param some_list: список товаров в маганах
        :return: минимальная стоимость товара из представленного списка товаров
        """
        try:
            mini = min(x.price_after_discount if x.price_after_discount else x.price for x in some_list)
        except ValueError:
            mini = 0
        return mini

    @classmethod
    def get_max_price(cls, some_list: List) -> int or float:
        """
        метод для получения максимальной стоимости товара из списка товаров
        :param some_list: список товаров в маганах
        :return: максимальная стоимость товара из представленного списка товаров
        """
        try:
            maxi = max(x.price_after_discount if x.price_after_discount else x.price for x in some_list)
        except ValueError:
            maxi = 100
        return maxi

    @classmethod
    def get_data_from_form(cls, request: HttpRequest) -> Dict:
        """
        метод для получения данных фильтра и тэга из параметров гет-запроса
        :param request: искомый запрос от клиента
        :return: словарь со значениями фильтров и тэга
        """
        filter_data = {
            'f_price': request.GET.get('price').split(';') if request.GET.get('price') else ['0', '1000000'],
            'f_title': request.GET.get('title') if request.GET.get('title') else '',
            'f_select': request.GET.get('select') if request.GET.get('select') and request.GET.get(
                'select') != 'seller' else '',
            'in_stock': 1 if request.GET.get('in_stock') and request.GET.get('in_stock') == '1' else 0,
            'ch_box_2': request.GET.get('ch_box_2') if request.GET.get('ch_box_2') else None,
            'tag': request.GET.get('tag') if request.GET.get('tag') else '',
        }

        return filter_data
