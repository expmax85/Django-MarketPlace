from typing import List, Dict, Tuple, Any

from django.core.cache import cache
from django.http import HttpRequest
from django.db.models import Count, QuerySet

from goods_app.models import ProductCategory, Product
from stores_app.models import SellerProduct


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
            some_list = []

        if sort_type == 'pop_dec':
            next_state = 'pop_inc'
            some_list = []

        if sort_type == 'newness_inc':
            next_state = 'newness_dec'
            some_list = cls.sort_by_newness(some_list, False)

        if sort_type == 'newness_dec':
            next_state = 'newness_inc'
            some_list = cls.sort_by_newness(some_list, True)

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
        # return sorted(some_list, key=lambda x: x.price_after_discount if x.price_after_discount else x.price,
        #               reverse=direction)
        return sorted(some_list, key=lambda x: x.price,
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
            # mini = min(x.price_after_discount if x.price_after_discount else x.price for x in some_list)
            mini = min(x.price for x in some_list)

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
            # maxi = max(x.price_after_discount if x.price_after_discount else x.price for x in some_list)
            maxi = max(x.price for x in some_list)

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
