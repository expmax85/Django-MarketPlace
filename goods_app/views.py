from typing import Dict, Callable

from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from banners_app.services import banner
from goods_app.forms import ReviewForm
from goods_app.models import Product
from goods_app.services import get_reviews, calculate_product_rating, context_pagination


class IndexView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs) -> Dict:
        context = super(IndexView, self).get_context_data(**kwargs)
        context['banners'] = banner()
        return context


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
