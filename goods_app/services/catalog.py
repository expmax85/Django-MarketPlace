from typing import List, Dict, Tuple

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models import Count, QuerySet, Q
from taggit.models import Tag

from goods_app.models import ProductCategory
from stores_app.models import SellerProduct
from discounts_app.services import get_discounted_prices_for_seller_products


class CatalogByCategoriesMixin:
    """
    класс-миксин для классбэйсд вью, для всех необходимых действий с каталогом
    """

    @classmethod
    def simple_sort(cls, some_list: List, sort_type: str) -> Tuple:
        """
        метод сортирует входящую последовательность в соответствии с заданным типом м направлением сортировки
        :param some_list: входящая последовательность для сортировки
        :param sort_type: тип сортировки - указывает на поле, по которому будет
        осуществляться сортировка и направление(возрастание/убывание)
        :return:    some_list - отсортированный массив
                    next_state - следующее состояние типа сортировки(т.к. направление
                    сортировки меняется при повторном нажатии)
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
            some_list = cls.sort_by_pop(some_list, False)

        if sort_type == 'pop_dec':
            next_state = 'pop_inc'
            some_list = cls.sort_by_pop(some_list, True)

        if sort_type == 'newness_inc':
            next_state = 'newness_dec'
            some_list = cls.sort_by_newness(some_list, False)

        if sort_type == 'newness_dec':
            next_state = 'newness_inc'
            some_list = cls.sort_by_newness(some_list, True)

        return some_list, next_state

    @classmethod
    def add_sale_prices_in_goods_if_needed(cls, some_goods: QuerySet) -> List:
        """метод расчитывает и добавляет к товару стоимость с учётом скидки, при её наличии"""
        goods_with_sale = get_discounted_prices_for_seller_products(some_goods)
        result = []
        for elem in goods_with_sale:

            if elem[1] is not None:
                elem[0].price_after_discount = round(elem[1], 2)
                elem[0].total = round(elem[1], 2)
                elem[0].sale = '1'
                elem[0].discount = elem[2]
                result.append(elem[0])

            else:
                elem[0].total = elem[0].price
                elem[0].sale = '0'
                result.append(elem[0])

        return result

    @classmethod
    def get_full_data(cls, tag: str = '', search: str = '', slug: str = '') -> Tuple[QuerySet or List, List, List]:
        """метод возвращвет все товары или товары по тэгу или товары подходящие под запрос из строки поиска"""

        if tag:
            goods = cls.get_data_by_tag(tag)

        elif slug:
            goods = cls.get_data_by_slug(slug)

        elif search:
            goods = cls.get_data_by_search_query(search)

        else:
            goods = SellerProduct.objects.all()

        sellers, tags = cls.get_sellers_and_tags(some_goods=goods, main_tag=tag)

        return goods, sellers, tags

    @classmethod
    def get_data_by_slug(cls, some_slug: str) -> QuerySet:
        """метод возвращает список товаров по слагу"""
        acceptable_categories = ProductCategory.objects.get(slug=some_slug).get_children() \
            if ProductCategory.objects.get(slug=some_slug).get_children() \
            else [ProductCategory.objects.get(slug=some_slug)]

        return SellerProduct.objects.select_related('product', 'seller', ) \
            .prefetch_related('product__category', 'product__tags') \
            .filter(
            product__category__in=acceptable_categories
        ).annotate(Count('product__product_comments'))

    @classmethod
    def get_data_by_tag(cls, some_tag: str) -> QuerySet:
        """метод возвращает список товаров по тэгу"""

        return SellerProduct.objects.select_related('product', 'seller', ) \
            .prefetch_related('product__category', 'product__tags') \
            .filter(
            product__tags__name__icontains=some_tag
        ).annotate(Count('product__product_comments'))

    @classmethod
    def get_data_by_search_query(cls, some_search_query: str) -> QuerySet:
        """метод возвращает список товаров по запросу из строки поиска"""

        return SellerProduct.objects.select_related('product', 'seller', ) \
            .prefetch_related('product__category', 'product__tags') \
            .filter(
            Q(product__name__icontains=some_search_query) |
            Q(product__category__name__icontains=some_search_query) |
            Q(product__tags__name__icontains=some_search_query) |
            Q(seller__name__icontains=some_search_query)
        ).annotate(Count('product__product_comments'))

    @classmethod
    def choose_popular_tags(cls, tags_list: List[Tag]) -> List:
        """метод возвращает 6 самых популярных тегов из списка"""
        pre_sort = []
        for el in tags_list:
            pre_sort.append((el, tags_list.count(el)))

        the_most_popular_tags = sorted(list(set(pre_sort)), key=lambda x: x[1], reverse=True)
        if len(the_most_popular_tags) <= 6:
            return [tag[0] for tag in the_most_popular_tags]
        return [tag[0] for tag in the_most_popular_tags][:6]

    @classmethod
    def filtering_data(cls, some_goods: QuerySet, filter_data: Dict) -> QuerySet:
        """фильтрует товары в соответсвии с данными формы фильтров"""
        print(f'filter*** {filter_data}')
        print(f'start*** {some_goods}')
        some_goods = some_goods.filter(
            seller__name__icontains=filter_data['f_select'],
            product__name__icontains=filter_data['f_title'],
            quantity__gte=filter_data['in_stock'],
            product__limited__icontains=filter_data['is_hot'],
        ).annotate(Count('product__product_comments'))
        print(f'big filter*** {some_goods}')
        if filter_data.get('tag', False):
            some_goods = some_goods.filter(
                product__tags__name=filter_data['tag'],
            )
        print(f'tag*** {some_goods}')
        if filter_data['f_price'][0] and filter_data['f_price'][1]:
            some_goods = cls.filtering_by_price(filter_data, some_goods)
        print(f'price*** {some_goods}')

        return some_goods

    @classmethod
    def get_full_data_with_filters(cls, search_query: str or None, search_tag: str or None, slug: str, filter_data: Dict
                                   ) -> Tuple:
        """
        метод для получения всех необходимых данных для отрисовки каталога с фильтрами
        :param search_query: пользовательский запрос из поисковой строки
        :param search_tag: пользовательский тэг для поиска всех товаров независимо от категории
        :param filter_data: словарь со значениями фильтров для отображения карточек товаров в магазинах
        :param slug: слаг категории товаров

        :return:    items_for_catalog - список товаров из магазина для отрисовки в каталоге
                    sellers - список уникальных продавцов
        """

        if search_tag:
            goods = cls.get_data_by_tag(search_tag)
        elif search_query:
            goods = cls.get_data_by_search_query(search_query)
        elif slug:
            goods = cls.get_data_by_slug(slug)
        else:
            goods = SellerProduct.objects.all()

        goods = cls.filtering_data(goods, filter_data)
        sellers, tags = cls.get_sellers_and_tags(goods, search_tag)

        return goods, sellers, tags

    @classmethod
    def get_sellers_and_tags(cls, some_goods: QuerySet, main_tag: str = '') -> Tuple[List, List]:
        """метод возвращает уникальных продавцов и тэги по списку товаров"""
        sellers = []
        tags = []

        for good in some_goods:
            if good.seller not in sellers:
                sellers.append(good.seller)

            for tag in good.product.tags.all():
                if tag not in tags and tag.name != main_tag:
                    tags.append(tag)

        tags = cls.choose_popular_tags(tags)
        return sellers, tags

    @classmethod
    def filtering_by_price(cls, filter_data: dict, some_goods_list: QuerySet) -> List:
        """метод фильтрации списка товаров по минимальной и максимальной стоимостям"""

        mini = int(filter_data['f_price'][0], 0)
        maxi = int(filter_data['f_price'][1], 0)

        goods_with_price = cls.add_sale_prices_in_goods_if_needed(some_goods_list)
        result_goods = []

        for elem in goods_with_price:
            if mini <= elem.total <= maxi:
                result_goods.append(elem)

        return result_goods

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
    def sort_by_pop(cls, some_list: List, direction: bool) -> List:
        """
        метод сортировки товаров в магазинах по количеству заказов
        :param some_list: исходный список товаров
        :param direction: направление сорировки; true - по возрастанию, false - по убыванию
        :return: отсортированный по наименованию список
        """
        return sorted(some_list, key=lambda x: len(x.order_products.all()), reverse=direction)

    @classmethod
    def sort_by_price(cls, some_list: List, direction: bool) -> List:
        return sorted(some_list, key=lambda x: x.total, reverse=direction)

    @classmethod
    def sort_by_amount_of_comments(cls, some_list: List, direction: bool) -> List:
        """
        метод сортировки товаров в магазинах по количеству комментариев
        :param some_list: исходный список товаров
        :param direction: направление сорировки; true - по возрастанию, false - по убыванию
        :return: отсортированный по количеству комментариев список
        """
        return sorted(some_list, key=lambda x: x.product.product_comments.count(), reverse=direction)

    @classmethod
    def sort_by_newness(cls, some_list: List, direction: bool) -> List:
        """
        метод сортировки товаров в магазинах по новизне
        :param some_list: исходный список товаров
        :param direction: направление сорировки; true - по возрастанию, false - по убыванию
        :return: отсортированный по новизне список
        """
        return sorted(some_list, key=lambda x: x.date_added, reverse=direction)

    @classmethod
    def get_min_price(cls, some_list: List) -> int or float:
        """
        метод для получения минимальной стоимости товара из списка товаров
        :param some_list: список товаров в маганах
        :return: минимальная стоимость товара из представленного списка товаров
        """
        try:
            mini = min([x.total for x in some_list])

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
            maxi = max([x.total for x in some_list])

        except ValueError:
            maxi = 10000
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
            'f_title': request.GET.get('title') if request.GET.get('title', None) else '',
            'f_select': request.GET.get('select') if request.GET.get('select', None) and request.GET.get(
                'select') != 'seller' else '',
            'in_stock': 1 if request.GET.get('in_stock', None) == '1' else 0,
            'is_hot': cls.get_is_hot_param(request),
            'tag': request.GET.get('tag') if request.GET.get('tag', None) else '',
        }

        return filter_data

    @classmethod
    def get_is_hot_param(cls, request: HttpRequest):
        if request.GET.get('is_hot', None) and request.GET.get('is_hot', None) == '1':
            return True
        else:
            return ''

    @classmethod
    def get_request_params_for_full_catalog(cls, request: HttpRequest) -> Tuple:
        """метод возвращает все все необходимые параметры гет-запроса для каталога без учета категории"""
        search = request.GET.get('query', None) \
            if request.GET.get('query', None) and request.GET.get('query', None) != 'undefined' else ''
        tag = request.GET.get('main_tag', None) if request.GET.get('main_tag', None) else ''
        sort_type = request.GET.get('sort_type', None) if request.GET.get('sort_type', None) else 'price_inc'
        page = request.GET.get('page', None) if request.GET.get('page', None) else 1
        slug = request.GET.get('slug', None) if request.GET.get('slug', None) else ''

        return search, tag, sort_type, page, slug

    @classmethod
    def check_if_filter_params(cls, request: HttpRequest) -> bool:
        """метод возвращает False если нет параметров фильтрации, иначе - True"""
        if not request.GET.get('price') and \
                not request.GET.get('title') and \
                not request.GET.get('select') and \
                not request.GET.get('in_stock') and \
                not request.GET.get('is_hot') and \
                not request.GET.get('tag'):
            return False
        return True

    @classmethod
    def custom_pagination_list(cls, paginator: Paginator, current_page: str or int) -> List:
        """ метод возвращает списов страниц для отрисовки. при большом количестве страниц, заменяет некоторую
            часть номеров (как в начале, так и в конце списка) страниц многоточиями
        """
        current_page = int(current_page)
        pages_list = list(range(1, paginator.num_pages + 1))
        if paginator.num_pages <= 9:
            return pages_list
        else:
            if current_page == 1:
                res = [*list(range(1, 7)), '...', pages_list[-1]]
                return res
            elif current_page in [2, 3, 4, 5]:
                res = [*list(range(1, current_page + 5)), '...', pages_list[-1]]
                return res
            elif current_page in [pages_list[-2], pages_list[-3], pages_list[-4], pages_list[-5]]:
                res = [1, '...', *list(range(current_page - 2, pages_list[-1] + 1))]
                return res
            elif current_page == pages_list[-1]:
                res = [1, '...', *list(range(current_page - 4, pages_list[-1] + 1))]
                return res
            else:
                res = [1, '...', *list(range(current_page - 2, current_page + 3)), '...', pages_list[-1]]
                return res


def get_categories() -> QuerySet:
    """
    Get all categories
    """
    categories_cache_key = 'categories:{}'.format('all')
    categories = cache.get(categories_cache_key)
    if not categories:
        categories = ProductCategory.objects.select_related('parent').all()
        cache.set(categories_cache_key, categories, 60 * 60)
    return categories
