from typing import Dict, Callable, Union, Iterable
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.http import JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

# from settings_app.config_project import OPTIONS
from settings_app.dynamic_preferences_registry import global_preferences_registry
from banners_app.services import banner
from goods_app.services.limited_products import random_product, \
    get_all_products, get_limited_products, get_random_categories, get_hot_offers
from goods_app.services.catalog import CatalogByCategoriesMixin
from goods_app.services.product_detail import CurrentProduct, context_pagination
from goods_app.forms import ReviewForm
from goods_app.models import Product
from stores_app.models import SellerProduct


class IndexView(ListView):
    """
    Main page view
    """
    model = SellerProduct
    template_name = 'index.html'
    context_object_name = 'products'
    global_preferences = global_preferences_registry.manager()

    def get_queryset(self) -> Iterable:
        # products = get_all_products(order_by=OPTIONS['general__sort_index'],
        #                             count=OPTIONS['general__count_popular_products'])
        products = get_all_products(order_by=self.global_preferences['general__sort_index'],
                                    count=self.global_preferences['general__count_popular_products'])

        return products

    def get_context_data(self, **kwargs) -> Dict:
        # limited_products = get_limited_products(count=OPTIONS['general__count_limited_products'])
        # random_product.days_duration = OPTIONS['general__days_duration']
        # random_product.time_update = OPTIONS['general__time_update']

        limited_products = get_limited_products(count=self.global_preferences['general__count_limited_products'])
        random_product.days_duration = self.global_preferences['general__days_duration']
        random_product.time_update = self.global_preferences['general__time_update']

        random_product.update_product(queryset=limited_products)

        context = {
            'banners': banner(),
            'limited_products': limited_products,
            'hot_offers': get_hot_offers(),
            'random_categories': get_random_categories(),
            **random_product.get_context_data(),
            **super().get_context_data(**kwargs)
        }
        return context


class ProductDetailView(DetailView):
    """
    Product detail view
    """
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'
    slug_url_kwarg = 'slug'
    global_preferences = global_preferences_registry.manager()

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        product = CurrentProduct(instance=context['product'])
        reviews = product.get_reviews
        context = {
            'reviews_count': reviews.count(),
            'comments': context_pagination(self.request, reviews,
                                           # size_page=OPTIONS['general__review_size_page']
                                           size_page=self.global_preferences['general__review_size_page']
                                           ),
            'form': ReviewForm(),
            **product.get_context_data('specifications', 'sellers', 'best_offer', 'tags'),
            **context
        }
        return context


def get_reviews(request: HttpRequest) -> JsonResponse:
    """
    View for getting reviews
    """
    slug = request.GET.get('slug')
    page = request.GET.get('page')
    product = CurrentProduct(slug=slug)
    reviews = product.get_reviews
    return JsonResponse({**product.get_review_page(reviews, page),
                         'slug': slug}, safe=False)


def post_review(request: HttpRequest) -> Union[JsonResponse, Callable]:
    """
    View for adding review
    """
    slug = request.POST.get('slug')
    product = CurrentProduct(slug=slug)
    form = ReviewForm(request.POST)
    global_preferences = global_preferences_registry.manager()

    if form.is_valid():
        form.save()
        product.calculate_product_rating()
        reviews = product.get_reviews
        paginator = Paginator(reviews,
                              # per_page=OPTIONS['general__review_size_page']
                              per_page=global_preferences['general__review_size_page']
                              )
        return JsonResponse({'num_pages': paginator.num_pages,
                             'slug': slug}, safe=False)
    elif form.errors.get('rating'):
        rating_error = _('You should to indicate the product rating')
        return JsonResponse({'num_pages': 0, 'rating_error': rating_error,
                             'slug': slug}, safe=False)
    return redirect(request.META.get('HTTP_REFERER'))


class CatalogByCategory(CatalogByCategoriesMixin, View):
    """
    класс-контроллер для отображения каталога-списка всех товаров в магазинах по определенной категории
    """

    def get(self, request, slug, page=1, sort_type='price_inc'):
        """
        метод для гет-запроса контроллера для отображения каталога товаров определенной категории
        :param request: искомый запрос
        :param slug: слаг необходимой категории товаров
        :param page: номер страницы пагинации для отображения
        :param sort_type: тип сортировки и её направление
        :return: рендер страницы каталога товаров определенной категории
        """
        # get data and sort this data
        row_items_for_catalog, category, sellers, tags = self.get_data_without_filters(slug)
        items_for_catalog, *_ = self.simple_sort(row_items_for_catalog, sort_type)

        # paginator
        paginator = Paginator(items_for_catalog, 8)
        page_obj = paginator.get_page(page)

        # custom levels for range input
        maxi = self.get_max_price(items_for_catalog)
        mini = self.get_min_price(items_for_catalog)
        midi = maxi / 2

        # next and previous buttons values
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)
        pages_list = list(range(1, paginator.num_pages + 1)) if paginator.num_pages > 1 else [1, ]

        return render(
            request,
            'goods_app/catalog.html',
            context={
                'category': category,
                'sellers': sellers,
                'page_obj': page_obj,
                'sort_type': sort_type,
                'mini': mini,
                'maxi': maxi,
                'midi': midi,
                'next_page': next_page,
                'prev_page': prev_page,
                'pages_list': pages_list,
                'tags': tags,
            })


class CardForAjax(CatalogByCategoriesMixin, View):
    """
    класс-контроллер для отображения набора товаров в каталоге с учетом необходимых фильтров, сортировки и пагинации
    без обновления изначальной страницы каталога
    """

    def get(self, request, slug, sort_type, page):
        """
        метод для гет-запроса контроллера для отображения  набора товаров в каталоге
        с учетом необходимых фильтров, сортировки и пагинации без обновления изначальной страницы каталога
        :param request: искомый запрос клиента
        :param slug: слаг необходимой категории товаров
        :param sort_type: тип сортировки и её направление
        :param page: номер страницы пагинации для отображения
        :return: json с ключами:
                html - текст разметки необходимых карточек товаров с учетов входных условий
                current_state - вид и направление текущей использованной сортировки
                next_state - тип и направление сортировки для повторного запроса
                next_page - значение следующей доступной страницы пагинации
                prev_page - значение предыдущей доступной страницы пагинации
                pages_list - список доступных номеров страниц пагинации при данных входных условиях
        """
        if not request.GET.get('price') and \
                not request.GET.get('title') and \
                not request.GET.get('select') and \
                not request.GET.get('in_stock') and \
                not request.GET.get('ch_box_2') and \
                not request.GET.get('tag'):
            # get data
            row_items_for_catalog, category, *_ = self.get_data_without_filters(slug)

        else:
            # get data and filter settings
            filter_data = self.get_data_from_form(request)
            row_items_for_catalog, category, sellers = self.get_data_with_filters(slug, filter_data)

        items_for_catalog, next_state = self.simple_sort(row_items_for_catalog, sort_type)

        # paginator
        paginator = Paginator(items_for_catalog, 8)
        pages_list = list(range(1, paginator.num_pages + 1)) if paginator.num_pages > 1 else [1, ]
        page_obj = paginator.get_page(page)

        # next and previous buttons values
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)

        context = {
            'pages_list': pages_list,
            'category': category,
            'page_obj': page_obj,
            'sort_type': sort_type,
            'next_page': next_page,
            'prev_page': prev_page,
        }

        return JsonResponse({
            'html': render_to_string('elems/good_card.html', context=context),
            'current_state': sort_type,
            'next_state': next_state,
            'next_page': next_page,
            'prev_page': prev_page,
            'pages_list': pages_list,
        })
