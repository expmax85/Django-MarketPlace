from typing import Dict, Callable, Union

from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from banners_app.services import banner
from goods_app.services import CatalogByCategoriesMixin, ProductMixin, \
    context_pagination, CurrentProduct, random_product
from goods_app.forms import ReviewForm
from goods_app.models import Product
from stores_app.models import SellerProduct


COUNT_REVIEWS_PER_PAGE = 3
TIME_UPDATE = '00:00'
DAYS_DURATION = 1


class IndexView(ProductMixin, ListView):
    model = SellerProduct
    template_name = 'index.html'
    context_object_name = 'products'

    def get_queryset(self):
        return self.get_seller_products()

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['banners'] = banner()
        random_product.set_days_duration(days_duration=DAYS_DURATION)
        random_product.set_time_update(time_update=TIME_UPDATE)
        context['special_product'] = random_product.update_product()
        context['update_time'] = random_product.get_end_time
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        product = CurrentProduct(instance=context['product'])
        reviews = product.get_reviews
        context['reviews_count'] = reviews.count()
        context['comments'] = context_pagination(self.request, reviews, size_page=COUNT_REVIEWS_PER_PAGE)
        context['form'] = ReviewForm()
        context = {**context, **product.get_context_data('specifications', 'sellers', 'best_offer', 'tags')}
        return context


def get_reviews(request) -> JsonResponse:
    slug = request.GET.get('slug')
    page = request.GET.get('page')
    product = CurrentProduct(slug=slug)
    reviews = product.get_reviews
    return JsonResponse({**product.get_review_page(reviews, page),
                         'slug': slug}, safe=False)


def post_review(request) -> Union[JsonResponse, Callable]:
    slug = request.POST.get('slug')
    product = CurrentProduct(slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        product.calculate_product_rating()
        reviews = product.get_reviews
        paginator = Paginator(reviews, per_page=COUNT_REVIEWS_PER_PAGE)
        return JsonResponse({'num_pages': paginator.num_pages,
                             'slug': slug}, safe=False)
    elif form.errors.get('rating'):
        rating_error = _('You should to indicate the product rating')
        return JsonResponse({'num_pages': 0, 'rating_error': rating_error,
                             'slug': slug}, safe=False)
    return redirect(request.META.get('HTTP_REFERER'))


class CatalogByCategory(CatalogByCategoriesMixin, View):

    def get(self, request, slug, sort_type, page):
        # get data and sort this data
        row_items_for_catalog, category = self.get_data_without_filters(slug)
        items_for_catalog = self.simple_sort(row_items_for_catalog, sort_type)

        # paginator
        paginator = Paginator(items_for_catalog, 8)
        page_obj = paginator.get_page(page)

        # custom levels for range input
        maxi = self.get_max_price(items_for_catalog)
        mini = self.get_min_price(items_for_catalog)
        midi = maxi / 2

        return render(
            request,
            'goods_app/catalog.html',
            context={
                'category': category,
                'page_obj': page_obj,
                'sort_type': sort_type,
                'mini': mini,
                'maxi': maxi,
                'midi': midi,
            })


class CatalogFilter(CatalogByCategoriesMixin, View):

    @method_decorator(csrf_protect)
    def post(self, request, slug, sort_type, page):
        # took data from filter-form
        filter_data = self.get_data_from_form(request)

        # get filtered data and sort this data
        row_items_for_catalog, category = self.get_data_with_filters(slug, filter_data)
        items_for_catalog = self.simple_sort(row_items_for_catalog, sort_type)

        # paginator
        paginator = Paginator(items_for_catalog, 8)
        page_obj = paginator.get_page(page)

        # custom levels for range input
        if not request.POST.get('price'):
            mini = self.get_min_price(items_for_catalog)
            maxi = self.get_max_price(items_for_catalog)
            midi = maxi // 2
        else:
            price_range = request.POST.get('price').split(';')
            mini = int(price_range[0])
            maxi = int(price_range[1])
            midi = maxi

        return render(
            request,
            'goods_app/catalog.html',
            context={
                'category': category,
                'page_obj': page_obj,
                'sort_type': sort_type,
                'mini': mini,
                'maxi': maxi,
                'midi': midi,
            })
