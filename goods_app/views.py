from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from typing import Dict, Callable

from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from banners_app.services import banner
from goods_app.services import CatalogByCategoriesMixin
from goods_app.models import ProductCategory
from goods_app.forms import ReviewForm
from goods_app.models import Product
from goods_app.services import get_reviews, calculate_product_rating, context_pagination
from orders_app.services import CartService
from stores_app.models import SellerProduct


class IndexView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'

    # Заглушка
    def get_queryset(self, queryset=None):
        return SellerProduct.objects.all()

    def get_context_data(self, **kwargs) -> Dict:
        context = super(IndexView, self).get_context_data(**kwargs)
        context['banners'] = banner()
        cart = CartService(self.request)
        context['total'] = cart.get_quantity()
        return context


# def index(request):
#     banners = banner()
#     return render(request, 'index.html', {'banners': banners,})


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        reviews = get_reviews(context['product'])
        context['reviews_count'] = reviews.count
        context['comments'] = context_pagination(self.request, reviews)
        context['form'] = ReviewForm()
        return context

    def post(self, request: HttpRequest, pk: int) -> Callable:
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            calculate_product_rating(product=self.get_object())
            return redirect(reverse('goods-polls:product-detail', kwargs={'pk': pk}))
        context = dict()
        context['form'] = form
        context['product'] = self.get_object()
        reviews = get_reviews(context['product'])
        context['reviews_count'] = reviews.count
        context['comments'] = context_pagination(self.request, reviews)
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
