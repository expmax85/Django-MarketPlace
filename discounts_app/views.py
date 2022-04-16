import datetime
from typing import Dict

from django.shortcuts import render
from django.views.generic import DetailView, ListView

from discounts_app.models import ProductDiscount
from discounts_app.services import get_discounted_prices_for_seller_products
from goods_app.services.product_detail import context_pagination


class DiscountsListView(ListView):
    """
    Страница со список всех действующих скидок

    ::Страница: Список всех скидок
    """

    def get(self, request, *args, **kwargs):
        discounts = ProductDiscount.objects.filter(is_active=True, valid_from__lte=datetime.date.today(),
                                                   valid_to__gte=datetime.date.today()) | \
                    ProductDiscount.objects.filter(is_active=True, valid_from=None,
                                                   valid_to=None) | \
                    ProductDiscount.objects.filter(is_active=True, valid_from=None,
                                                   valid_to__gte=datetime.date.today()) | \
                    ProductDiscount.objects.filter(is_active=True, valid_from__lte=datetime.date.today(),
                                                   valid_to=None)

        discounts = context_pagination(request, discounts, 4)
        return render(request, 'discounts_app/discounts_list.html', {'discounts': discounts})


class DiscountDetailView(DetailView):
    """
    Детальная страница скидки

    ::Страница: Детальная страница скидки
    """
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
