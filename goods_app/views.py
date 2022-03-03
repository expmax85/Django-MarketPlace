from typing import Dict, Callable
from django.core.paginator import Paginator
from django.db import connection, reset_queries
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from banners_app.services import banner
from goods_app.services import CatalogByCategoriesMixin, ProductMixin
from goods_app.forms import ReviewForm
from goods_app.models import Product
from goods_app.services import context_pagination
from stores_app.models import SellerProduct


class IndexView(ListView):
    model = SellerProduct
    template_name = 'index.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['banners'] = banner()
        return context


class ProductDetailView(DetailView, ProductMixin):
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        # reset_queries()
        reviews = self.get_reviews
        context['reviews_count'] = reviews.count
        context['comments'] = context_pagination(self.request, reviews)
        context['form'] = ReviewForm()
        self.update_context(context=context, elements=['specifications', 'sellers', 'tags'])
        return context

    def post(self, request: HttpRequest, slug: str) -> Callable:
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            self.calculate_product_rating()
            return redirect(reverse('goods-polls:product-detail', kwargs={'slug': slug}))
        context = dict()
        reviews = self.get_reviews
        context['reviews_count'] = reviews.count
        context['comments'] = context_pagination(self.request, reviews)
        context['product'] = self.get_object()
        context['form'] = form
        self.update_context(context=context, elements=['specifications', 'sellers', 'tags'])
        return render(request, 'goods_app/product_detail.html', context=context)


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
