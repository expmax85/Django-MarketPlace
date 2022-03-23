import datetime
from typing import Dict, Callable
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from banners_app.services import banner
from discounts_app.models import *


class DiscountsListView(ListView):
    model = Discount
    template_name = 'discounts_app/discounts_list.html'
    context_object_name = 'discounts'

    def get_queryset(self):
        discounts = []
        discounts += ProductDiscount.objects.filter(is_active=True, valid_from__lte=datetime.date.today(),
                                                    valid_to__gte=datetime.date.today())
        discounts += GroupDiscount.objects.filter(is_active=True, valid_from__lte=datetime.date.today(),
                                                  valid_to__gte=datetime.date.today())
        return discounts

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['banners'] = banner()
        # random_product.set_days_duration(days_duration=OPTIONS['general__days_duration'])
        # random_product.set_time_update(time_update=OPTIONS['general__time_update'])
        # context['special_product'] = random_product.update_product()
        # context['update_time'] = random_product.get_end_time
        return context


# class ProductDetailView(DetailView):
#     model = Product
#     context_object_name = 'product'
#     template_name = 'goods_app/product_detail.html'
#     slug_url_kwarg = 'slug'
#
#     def get_context_data(self, **kwargs) -> Dict:
#         context = super().get_context_data(**kwargs)
#         product = CurrentProduct(instance=context['product'])
#         reviews = product.get_reviews
#         context['reviews_count'] = reviews.count()
#         context['comments'] = context_pagination(self.request, reviews,
#                                                  size_page=OPTIONS['general__review_size_page'])
#         context['form'] = ReviewForm()
#         context = {**context, **product.get_context_data('specifications', 'sellers', 'best_offer', 'tags')}
#         return context
