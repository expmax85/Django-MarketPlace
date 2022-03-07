from decimal import Decimal
from typing import List

from django.core.exceptions import FieldError
from django.core.paginator import Paginator
from django.db.models import QuerySet, Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from taggit.models import Tag

from stores_app.models import SellerProduct, Seller

CATALOG_PAGE_SIZE = 12
BASE_SORT_LIST = [
    'price_after_discount',
    'product__product_comments__count',
    'date_added'
]


class DefSortType:
    """
    Класс для определения последнего выбранного типа сортировки
    """

    def __init__(self) -> None:
        self._previous = []
        self._sort_type = None
        self._pre_result = None

    def define_sort_type(self, sort_list: List) -> None:
        self._previous.append(sort_list)
        if len(self._previous) >= 2:
            self._previous = self._previous[-2:]
            set1 = (*self._previous[0],)
            set2 = (*self._previous[1],)
            self._pre_result = set.difference(set(set2), set(set1))
        elif len(self._previous) == 1:
            self._pre_result = self._previous[0]
        try:
            self._sort_type = list(self._pre_result)[0]
        except IndexError:
            pass

    @property
    def get_sort_type(self) -> List:
        return self._sort_type


Type_sorting = DefSortType()


class JsonFilterStore(ListView):
    """
    Фильтр с использованием jquery, ajax и hogan c частичным обновлением страницы.
    """
    model = SellerProduct
    context_object_name = 'products'
    template_name = 'goods_app/test-catalog.html'

    def get_queryset(self) -> QuerySet:
        try:
            price = self.request.GET.get('price').split(';')
            price_min = Decimal(price[0])
            price_max = Decimal(price[1])
        except AttributeError:
            category = self.request.GET.get('category', "")
            return SellerProduct.objects.select_related('product', 'discount', 'seller') \
                                .prefetch_related('product__category') \
                                .filter(product__category__name__icontains=category)
        if self.request.GET.get('in_stock') == 'on':
            stock = 1
        else:
            stock = 0
        if self.request.GET.get('tag'):
            queryset = SellerProduct.objects.select_related('product', 'seller', 'discount') \
                                    .prefetch_related('product__category') \
                                    .filter(product__tags__name__in=[str(self.request.GET.get('tag'))]) \
                                    .annotate(Count('product__product_comments'))
        else:
            queryset = SellerProduct.objects.select_related('product', 'seller', 'discount') \
                                    .prefetch_related('product__category') \
                                    .filter(seller__name__icontains=self.request.GET.get('seller', ""),
                                            product__name__icontains=self.request.GET.get('title', ""),
                                            product__category__name__icontains=self.request.GET.get('category', ""),
                                            price_after_discount__range=(price_min, price_max),
                                            quantity__gte=stock) \
                                    .annotate(Count('product__product_comments'))
        return queryset

    def get(self, request, *args, **kwargs) -> JsonResponse:
        queryset = self.get_queryset()
        base_list = self._sort_list(BASE_SORT_LIST)
        if base_list:
            Type_sorting.define_sort_type(base_list)
            queryset = queryset.order_by(str(Type_sorting.get_sort_type))
        try:
            queryset = queryset.values('id', 'product__category', 'product__name',
                                       'product__category__name', 'product__slug',
                                       'discount__percent', 'discount__amount', 'price',
                                       'price_after_discount', 'date_added',
                                       'product__product_comments__count')
        except FieldError:
            context = dict()
            context['sellers'] = Seller.objects.all()
            context['tags'] = Tag.objects.all()
            paginator = Paginator(queryset, per_page=CATALOG_PAGE_SIZE)
            page_number = request.GET.get('page', "")
            if page_number == "":
                page_number = 1
            page_obj = paginator.get_page(page_number)
            context['products'] = page_obj.object_list
            context['has_previous'] = page_obj.has_previous()
            context['previous_page_number'] = page_obj.number - 1
            context['num_pages'] = page_obj.paginator.num_pages
            context['number'] = page_obj.number
            context['has_next'] = page_obj.has_next()
            context['next_page_number'] = page_obj.number + 1
            return render(request, 'goods_app/test-catalog.html', context=context)
        paginator = Paginator(queryset, per_page=CATALOG_PAGE_SIZE)
        page_number = request.GET.get('page', "")
        if page_number == "":
            page_number = 1
        page_obj = paginator.get_page(page_number)
        return JsonResponse({'products': list(page_obj.object_list),
                             'has_previous': None if page_obj.has_previous() is False
                             else "previous",
                             'previous_page_number': page_obj.number - 1,
                             'num_pages': page_obj.paginator.num_pages,
                             'number': page_obj.number,
                             'has_next': None if page_obj.has_next() is False
                             else "next",
                             'next_page_number': page_obj.number + 1}, safe=False)

    def _sort_list(self, params: List) -> List:
        """Форирование списка полей, по которым производится соритровка"""
        list_order = []
        for item in params:
            try:
                value = int(self.request.GET.get(str(item)))
                if value == 0:
                    list_order.append("".join(['-', str(item)]))
                else:
                    list_order.append(str(item))
            except ValueError:
                pass
            except TypeError:
                pass
        return list_order
