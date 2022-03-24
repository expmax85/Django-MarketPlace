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
from discounts_app.services import get_discounted_prices_for_seller_products
from stores_app.models import SellerProduct


class DiscountsListView(ListView):
    template_name = 'discounts_app/discounts_list.html'
    context_object_name = 'discounts'

    def get_queryset(self):
        discounts = []
        discounts += ProductDiscount.objects.filter(is_active=True, valid_from__lte=datetime.date.today(),
                                                    valid_to__gte=datetime.date.today())
        # discounts += GroupDiscount.objects.filter(is_active=True, valid_from__lte=datetime.date.today(),
        #                                           valid_to__gte=datetime.date.today())
        return discounts


class DiscountDetailView(DetailView):
    model = ProductDiscount
    context_object_name = 'discount'
    template_name = 'discounts_app/discount_detail.html'
    slug_url_kwarg = 'slug'
    id_url_kwarg = 'id'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        discount = context['discount']
        products = discount.seller_products.all()
        products = get_discounted_prices_for_seller_products(products, default_discount=discount)
        context['products'] = products
        return context
