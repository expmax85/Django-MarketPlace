from typing import Dict, Callable, Union
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from banners_app.services import banner
from goods_app.services import CatalogByCategoriesMixin, ProductMixin, \
    context_pagination, CurrentProduct
from goods_app.forms import ReviewForm
from goods_app.models import Product
from stores_app.models import SellerProduct


COUNT_REVIEWS_PER_PAGE = 3


class IndexView(ProductMixin, ListView):
    model = SellerProduct
    template_name = 'index.html'
    context_object_name = 'products'

    def get_queryset(self):
        return self.get_seller_products()

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['banners'] = banner()
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        product = CurrentProduct(instance=self.get_object())
        context['product'] = product.get_product
        reviews = product.get_reviews
        context['reviews_count'] = reviews.count()
        context['comments'] = context_pagination(self.request, reviews, size_page=COUNT_REVIEWS_PER_PAGE)
        context['form'] = ReviewForm()
        context['specifications'] = product.get_specifications
        context['sellers'] = product.get_sellers
        context['best_offer'] = product.get_best_seller
        context['tags'] = product.get_tags
        return context


def get_reviews(request) -> JsonResponse:
    if request.method == "GET":
        slug = request.GET.get('slug')
        page = request.GET.get('page')
        product = CurrentProduct(slug=slug)
        reviews = product.get_reviews
        reviews_count = reviews.count()
        reviews = reviews.values('author', 'content', 'added')
        paginator = Paginator(reviews, per_page=COUNT_REVIEWS_PER_PAGE)
        page_obj = paginator.get_page(page)
        empty_pages = None if page_obj.paginator.num_pages < 2 else "not_empty"
        return JsonResponse({'comments': list(page_obj.object_list),
                             'has_previous': None if page_obj.has_previous() is False
                             else "previous",
                             'previous_page_number': page_obj.number - 1,
                             'num_pages': page_obj.paginator.num_pages,
                             'number': page_obj.number,
                             'has_next': None if page_obj.has_next() is False
                             else "next",
                             'next_page_number': page_obj.number + 1,
                             'empty_pages': empty_pages,
                             'slug': slug,
                             'reviews_count': reviews_count}, safe=False)


def post_review(request) -> Union[JsonResponse, Callable]:
    slug = request.POST.get('slug')
    product = CurrentProduct(slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        product.calculate_product_rating()
        reviews = product.get_reviews
        paginator = Paginator(reviews, per_page=COUNT_REVIEWS_PER_PAGE)
        num_pages = paginator.num_pages
        return JsonResponse({'num_pages': num_pages,
                             'slug': slug}, safe=False)
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


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
