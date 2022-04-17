from typing import Dict, Callable, Union, Iterable

from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView

from goods_app.services.catalog import CatalogByCategoriesMixin
from settings_app.dynamic_preferences_registry import global_preferences_registry
from banners_app.services import banner
from goods_app.services.limited_products import random_product, \
    get_all_products, get_limited_products, get_random_categories, get_hot_offers
from goods_app.services.product_detail import CurrentProduct, context_pagination
from goods_app.forms import ReviewForm
from goods_app.models import Product
from stores_app.models import SellerProduct


class IndexView(ListView):
    """
    Главная страница

    ::Страница: Главная
    """
    model = SellerProduct
    template_name = 'goods_app/index.html'
    context_object_name = 'products'

    def get_queryset(self) -> Iterable:
        OPTIONS = global_preferences_registry.manager().by_name()
        products = get_all_products(count=OPTIONS['count_popular_products'])
        return products

    def get_context_data(self, **kwargs) -> Dict:
        OPTIONS = global_preferences_registry.manager().by_name()
        limited_products = get_limited_products(count=OPTIONS['count_limited_products'])
        if limited_products:
            random_product.days_duration = OPTIONS['days_duration']
            random_product.time_update = OPTIONS['time_update']
            random_product.update_product(queryset=get_limited_products())
        context = {
            'banners': banner(),
            'limited_products': limited_products,
            'hot_offers': get_hot_offers(count=OPTIONS['count_hot_offers']),
            'random_categories': get_random_categories(),
            **random_product.get_context_data(),
            **super().get_context_data(**kwargs),
        }
        return context


class ProductDetailView(DetailView):
    """
    Детальная страница продукта

    ::Страница: Детальная страница продукта
    """
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        OPTIONS = global_preferences_registry.manager().by_name()
        context = super().get_context_data(**kwargs)
        product = CurrentProduct(instance=context['product'])
        reviews = product.get_reviews

        context = {
            'reviews_count': reviews.count(),
            'comments': context_pagination(self.request, reviews,
                                           size_page=OPTIONS['review_size_page']),

            'form': ReviewForm(),
            'specifications': product.get_specifications,
            'sellers': product.get_sellers,
            'tags': product.get_tags,
            **product.get_calculate_prices(),
            **context
        }
        return context


def get_reviews(request: HttpRequest) -> JsonResponse:
    """
    Представление для получения всех отзывов о товаре

    ::Страница: Детальная страница продукта
    """
    slug = request.GET.get('slug')
    page = request.GET.get('page')
    product = CurrentProduct(slug=slug)
    reviews = product.get_reviews
    return JsonResponse({**product.get_review_page(reviews, page),
                         'slug': slug}, safe=False)


def post_review(request: HttpRequest) -> Union[JsonResponse, Callable]:
    """
    Представление для добавления отзыва о

    ::Страница: Детальная страница продукта
    """
    slug = request.POST.get('slug')
    product = CurrentProduct(slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        product.update_product_rating()
        reviews = product.get_reviews
        OPTIONS = global_preferences_registry.manager().by_name()
        paginator = Paginator(reviews, per_page=OPTIONS['review_size_page'])
        return JsonResponse({'num_pages': paginator.num_pages,
                             'slug': slug}, safe=False)
    elif form.errors.get('rating'):
        rating_error = _('You should to indicate the product rating')
        return JsonResponse({'num_pages': 0, 'rating_error': rating_error,
                             'slug': slug}, safe=False)
    return redirect(request.META.get('HTTP_REFERER'))


class FullCatalogView(CatalogByCategoriesMixin, View):
    """
    Класс-контроллер для отображения каталога-списка всех товаров

    ::Страница: Каталог
    """

    def get(self, request):
        """
        метод для гет-запроса контроллера для отображения каталога всех товаров с учётом параметров гет-запроса
        возможные параметры
            search - запрос пользователя из поисковой строки
            tag - выбранный тэг
            sort_type - тип сортировки
            page - страница пагинации
            slug - слаг категории товаров
        :return: рендер страницы каталога товаров определенной категории
        """
        # получаем параметры гет-запроса
        search, tag, sort_type, page, slug = self.get_request_params_for_full_catalog(request)

        # получаем товары в соответсвии с параметрами гет-запроса
        row_items_for_catalog, sellers, tags = self.get_full_data(tag, search, slug)
        row_items_for_catalog = self.add_sale_prices_in_goods_if_needed(row_items_for_catalog)

        # сортируем товары
        items_for_catalog, *_ = self.simple_sort(row_items_for_catalog, sort_type)

        # пагинатор
        paginator = Paginator(items_for_catalog, 8)
        page_obj = paginator.get_page(page)

        # кастомные параметры для рэнж-инпута в фильтре каталога
        maxi = self.get_max_price(items_for_catalog)
        mini = self.get_min_price(items_for_catalog)
        midi = round((maxi + mini) / 2, 2)

        # настройка кнопок пагинации
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)
        pages_list = self.custom_pagination_list(paginator, page)

        return render(
            request,
            'goods_app/catalog.html',
            context={
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
                'search': search,
                'tag': tag,
            })


class AllCardForAjax(CatalogByCategoriesMixin, View):
    """
    Класс-контроллер для отображения набора товаров в каталоге с учетом необходимых фильтров, сортировки и пагинации

    ::Страница: Каталог
    """

    def get(self, request):
        """
        метод для гет-запроса контроллера для отображения  набора товаров в каталоге
        с учетом необходимых фильтров, сортировки и пагинации без обновления изначальной страницы каталога
        get параметры :
            search - запрос пользователя из поисковой строки
            tag - выбранный тэг
            sort_type - тип сортировки
            page - страница пагинации
            slug - слаг категории товаров
        :param request: искомый запрос клиента

        :return: json с ключами:
                html - текст разметки необходимых карточек товаров с учетов входных условий
                current_state - вид и направление текущей использованной сортировки
                next_state - тип и направление сортировки для повторного запроса
                next_page - значение следующей доступной страницы пагинации
                prev_page - значение предыдущей доступной страницы пагинации
                pages_list - список доступных номеров страниц пагинации при данных входных условиях
        """

        search, tag, sort_type, page, slug = self.get_request_params_for_full_catalog(request)

        if not self.check_if_filter_params(request):
            # получаем товары без фильтра и актуальные стоимости
            row_items_for_catalog, sellers, tags = self.get_full_data(tag, search, slug)
            row_items_for_catalog = self.add_sale_prices_in_goods_if_needed(row_items_for_catalog)

        else:
            # получаем товары с фильтром и актуальные стоимости
            filter_data = self.get_data_from_form(request)
            row_items_for_catalog, sellers, tags = self.get_full_data_with_filters(
                search_query=search,
                search_tag=tag,
                slug=slug,
                filter_data=filter_data
            )

        items_for_catalog, next_state = self.simple_sort(row_items_for_catalog, sort_type)

        # пагинатор
        paginator = Paginator(items_for_catalog, 8)

        pages_list = self.custom_pagination_list(paginator, page)
        page_obj = paginator.get_page(page)

        # кнопки пагинации
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)

        context = {
            'pages_list': pages_list,
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
            'sort_type': sort_type,
        })
