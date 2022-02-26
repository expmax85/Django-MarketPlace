from typing import List, Dict, Tuple, Any

from django.http import HttpRequest
from goods_app.models import ProductCategory
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet
from goods_app.models import Product, ProductComment


def calculate_product_rating(product: 'Product') -> None:
    rating = ProductComment.objects.only('rating').filter(product_id=product.id).aggregate(Avg('rating'))['rating__avg']
    if rating:
        product.rating = round(float(rating), 0)
        product.save(update_fields=['rating'])

# TODO сервис добавления комментариев к товару
def create_comment(request: HttpRequest) -> None:
    pass

def get_reviews(product: 'Product'):
    reviews_cache_key = 'reviews:{}'.format(product.id)
    reviews = cache.get(reviews_cache_key)
    if not reviews:
        reviews = product.product_comments.all()
        cache.set(reviews_cache_key, reviews, 120 * 60)
    return reviews


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

    @classmethod
    def simple_sort(cls, some_list: List, sort_type: str) -> List:

        if sort_type == 'name_inc':
            some_list = cls.sort_by_name(some_list, False)

        if sort_type == 'name_dec':
            some_list = cls.sort_by_name(some_list, True)

        if sort_type == 'price_inc':
            some_list = cls.sort_by_price(some_list, False)

        if sort_type == 'price_dec':
            some_list = cls.sort_by_price(some_list, True)

        if sort_type == 'comment_inc':
            some_list = cls.sort_by_amount_of_comments(some_list, False)

        if sort_type == 'comment_dec':
            some_list = cls.sort_by_amount_of_comments(some_list, True)

        return some_list

    @classmethod
    def get_data_without_filters(cls, slug: str) -> Tuple[List, Any]:
        category = ProductCategory.objects.prefetch_related('products', 'products__seller_products').get(slug=slug)
        products_set = category.products.all()
        items_for_catalog = []

        for elem in products_set:
            items_for_catalog.extend(elem.seller_products.all())

        return items_for_catalog, category

    @classmethod
    def get_data_with_filters(cls, slug: str, filter_data: Dict) -> Tuple[List, Any]:
        category = ProductCategory.objects.prefetch_related('products', 'products__seller_products').get(slug=slug)
        products_set = category.products.all()

        items_for_catalog = []

        for elem in products_set:

            if not filter_data['f_title'] and filter_data['f_price']:
                items_for_catalog.extend(elem.seller_products.filter(
                    price__in=list(range(int(filter_data['f_price'][0]), int(filter_data['f_price'][1])))))

            if filter_data['f_title'] and not filter_data['f_price']:
                if filter_data['f_title'].lower in elem.name.lower():
                    items_for_catalog.extend(elem.seller_products)

            if filter_data['f_title'] and filter_data['f_price']:
                if filter_data['f_title'].lower in elem.name.lower():
                    items_for_catalog.extend(elem.seller_products.filter(
                        price__in=list(range(int(filter_data['f_price'][0]), int(filter_data['f_price'][1])))))

        return items_for_catalog, category

    @classmethod
    def sort_by_name(cls, some_list: List, direction: bool) -> List:
        return sorted(some_list, key=lambda x: x.product.name, reverse=direction)

    @classmethod
    def sort_by_price(cls, some_list: List, direction: bool) -> List:
        return sorted(some_list, key=lambda x: x.price_after_discount if x.price_after_discount else x.price,
                      reverse=direction)

    @classmethod
    def sort_by_amount_of_comments(cls, some_list: List, direction: bool) -> List:
        return sorted(some_list, key=lambda x: x.product.comments, reverse=direction)

    @classmethod
    def get_min_price(cls, some_list: List) -> int or float:
        try:
            mini = min(x.price_after_discount if x.price_after_discount else x.price for x in some_list)
        except ValueError:
            mini = 0
        return mini

    @classmethod
    def get_max_price(cls, some_list: List) -> int or float:
        try:
            maxi = max(x.price_after_discount if x.price_after_discount else x.price for x in some_list)
        except ValueError:
            maxi = 100
        return maxi

    @classmethod
    def get_data_from_form(cls, request: HttpRequest) -> Dict:
        filter_data = {
            'f_price': request.POST.get('price').split(';') if request.POST.get('price') else None,
            'f_title': request.POST.get('title') if request.POST.get('title') else None,
            'f_select': request.POST.get('select') if request.POST.get('select') else None,
            'ch_box_1': request.POST.get('ch_box_1') if request.POST.get('ch_box_1') else None,
            'ch_box_2': request.POST.get('ch_box_2') if request.POST.get('ch_box_2') else None,
        }

        return filter_data
