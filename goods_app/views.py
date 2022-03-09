from typing import Dict, Callable
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.http import HttpRequest, JsonResponse
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

    def get_queryset(self):
        return SellerProduct.objects.select_related('seller', 'product', 'discount', 'product__category').all()

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['banners'] = banner()
        return context


class ProductDetailView(ProductMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'goods_app/product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_object()
        reviews = self.get_reviews(product=self.get_object())
        context['reviews_count'] = reviews.count
        context['comments'] = context_pagination(self.request, reviews)
        context['form'] = ReviewForm()
        context['specifications'] = self.get_specifications(context['product'])
        context['sellers'] = self.get_sellers(context['product'])
        context['best_offer'] = self.get_best_seller(context['product'])
        context['tags'] = self.get_tags(context['product'])
        return context

    # def post(self, request: HttpRequest, slug: str) -> Callable:
    #     form = ReviewForm(request.POST)
    #     product = self.get_object()
    #     if form.is_valid():
    #         form.save()
    #         self.calculate_product_rating(product)
    #         return redirect(reverse('goods-polls:product-detail', kwargs={'slug': slug}))
    #     context = dict()
    #     context['product'] = product
    #     reviews = self.get_reviews(product)
    #     context['reviews_count'] = reviews.count
    #     context['comments'] = context_pagination(self.request, reviews)
    #     context['specifications'] = self.get_specifications(product)
    #     context['sellers'] = self.get_sellers(product)
    #     context['tags'] = self.get_tags(product)
    #     context['form'] = form
    #     return render(request, 'goods_app/product_detail.html', context=context)


def get_reviews(request):
    if request.method == "GET":
        slug = request.GET.get('slug')
        page = request.GET.get('page')
        product = Product.objects.get(slug=slug)
        reviews = product.product_comments.all()
        reviews = reviews.values('author', 'content', 'added')
        paginator = Paginator(reviews, per_page=3)
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
                             'slug': slug}, safe = False)


def post_review(request):
    product_id = request.POST.get('product')
    slug = request.POST.get('slug')
    product = Product.objects.get(id=product_id)
    form = ReviewForm(request.POST)
    print('ok')
    if form.is_valid():
        form.save()
        fr = ProductMixin()
        print('ok')
        fr.calculate_product_rating(product=product)
        reviews = product.product_comments.all()
        reviews = reviews.values('author', 'content', 'added')
        paginator = Paginator(reviews, per_page=3)
        page_obj = paginator.get_page(paginator.num_pages)
        empty_pages = None if page_obj.paginator.num_pages < 2 else "not_empty"
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        # return JsonResponse({'comments': list(page_obj.object_list),
        #                      'has_previous': None if page_obj.has_previous() is False
        #                      else "previous",
        #                      'previous_page_number': page_obj.number - 1,
        #                      'num_pages': page_obj.paginator.num_pages,
        #                      'number': page_obj.number,
        #                      'has_next': None if page_obj.has_next() is False
        #                      else "next",
        #                      'next_page_number': page_obj.number + 1,
        #                      'empty_pages': empty_pages,
        #                      'slug': slug}, status = 200)



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
