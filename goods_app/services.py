import random
import datetime as dt
from typing import List, Dict, Tuple, Any

from django.apps import apps
from django.http import HttpRequest
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet

from goods_app.models import ProductCategory, ProductComment, Product
from stores_app.models import SellerProduct


COUNT_REVIEWS_PER_PAGE = 3


class RandomProduct:

    def __init__(self, model, time_update='00:00', days_duration=1, fallibility=1):
        self.model = apps.get_model(model.split('.')[0], model.split('.')[1])
        self.queryset = self.model.objects.all()
        self.days_duration = days_duration
        self.fallibility = dt.timedelta(days=fallibility)
        self.product = random.choice(list(self.queryset))
        today = dt.date.today()
        date = " ".join([str(today.strftime("%d.%m.%Y")), time_update])
        self.end_time = dt.datetime.strptime(date, "%d.%m.%Y %H:%M")

    def update_product(self):
        if dt.datetime.now() >= self.end_time:
            self.product = random.choice(list(self.queryset))
            self.end_time += dt.timedelta(days=self.days_duration)
        return self.product

    def set_time_update(self, time_update):
        today = dt.date.today()
        date = " ".join([str(today.strftime("%d.%m.%Y")), time_update])
        self.end_time = dt.datetime.strptime(date, "%d.%m.%Y %H:%M")

    def set_days_duration(self, days_duration):
        self.days_duration = days_duration

    @property
    def get_end_time(self):
        return str((self.end_time + self.fallibility).strftime("%d.%m.%Y %H:%M"))


random_product = RandomProduct('stores_app.SellerProduct')


class CurrentProduct:

    def __init__(self, **kwargs):
        if 'slug' in kwargs:
            self.product = Product.objects.get(slug=kwargs['slug'])
        elif 'instance' in kwargs:
            self.product = kwargs['instance']
        else:
            raise ValueError

    @property
    def get_product(self):
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
        return self.product.specifications.all()

    @property
    def get_tags(self) -> QuerySet:
        return self.product.tags.all()

    @property
    def get_reviews(self) -> QuerySet:
        reviews_cache_key = 'reviews:{}'.format(self.product.id)
        reviews = cache.get(reviews_cache_key)
        if not reviews:
            reviews = self.product.product_comments.all()
            cache.set(reviews_cache_key, reviews, 60)
        return reviews

    def get_review_page(self, queryset: QuerySet, page: int) -> Dict:
        reviews_count = queryset.count()
        reviews = queryset.values('author', 'content', 'added')
        paginator = Paginator(reviews, per_page=COUNT_REVIEWS_PER_PAGE)
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

    def get_context_data(self, *args):
        context = dict()
        for arg in args:
            try:
                context[str(arg)] = getattr(self, ''.join(['get_', str(arg)]))
            except AttributeError as err:
                raise AttributeError(err)
        return context


class ProductMixin:

    @classmethod
    def get_seller_products(cls, *kwargs) -> QuerySet:
        return SellerProduct.objects.select_related('seller', 'product', 'discount', 'product__category').all()

    @classmethod
    def get_special_offer(cls, products: QuerySet) -> QuerySet:
        return random.choice(list(products))


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
