from typing import Callable, Dict

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from stores_app.forms import *
from stores_app.models import Seller
from stores_app.services import QueryMixin


CREATE_SP_ERROR = 150


class SellersRoomView(LoginRequiredMixin, PermissionRequiredMixin, QueryMixin, ListView):
    """Page for view seller room for Sellers-group"""
    permission_required = ('profiles_app.Sellers',)
    model = Seller
    template_name = 'stores_app/sellers_room.html'
    context_object_name = 'stores'

    def get_queryset(self) -> 'QuerySet':
        return self.get_user_stores(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.get_categories()
        context['seller_products'] = self.get_seller_products(user=self.request.user)
        return context


class AddNewStoreView(LoginRequiredMixin, PermissionRequiredMixin, QueryMixin, View):
    """Page for create new store"""
    permission_required = ('profiles_app.Sellers',)

    def get(self, request) -> Callable:
        form = AddStoreForm()
        return render(request, 'stores_app/add_store.html', context={'form': form})

    def post(self, request) -> Callable:
        form = AddStoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('stores-polls:sellers-room'))
        form = AddStoreForm()
        return render(request, 'stores_app/add_store.html', context={'form': form})


class StoreDetailView(LoginRequiredMixin, PermissionRequiredMixin, QueryMixin, DetailView):
    """Page for view and edit detail store"""
    permission_required = ('profiles_app.Sellers',)
    context_object_name = 'store'
    template_name = 'stores_app/store_detail.html'
    model = Seller
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data()
        context['form'] = EditStoreForm(instance=self.get_object())
        return context

    def post(self, request, slug) -> Callable:
        form = EditStoreForm(request.POST, request.FILES, instance=self.get_object())
        if form.is_valid():
            form.save()
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:store_detail', kwargs={'slug': slug}))


class AddSellerProductView(LoginRequiredMixin, PermissionRequiredMixin, QueryMixin, View):
    """Page for adding new seller product"""
    permission_required = ('profiles_app.Sellers',)

    def get_queryset(self, request):
        category_id = request.GET.get('category_id')
        return self.get_products(category_id=category_id)

    def get(self, request):
        context = dict()
        context['products'] = self.get_queryset(request)
        context['discounts'] = self.get_discounts()
        context['stores'] = self.get_user_stores(user=request.user)
        context['form'] = AddSellerProductForm()
        return render(request, 'stores_app/new_product_in_store.html', context=context)

    def post(self, request):
        form = AddSellerProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('stores-polls:sellers-room'))
        else:
            messages.add_message(request, CREATE_SP_ERROR, form.errors)
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class SelleProductDetailView(DetailView):
    pass


@permission_required('profiles_app.Sellers')
def remove_Store(request):
    if request.method == 'GET':
        QueryMixin.remove_store(request)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@permission_required('profiles_app.Sellers')
def remove_SellerProduct(request):
    if request.method == 'GET':
        QueryMixin.remove_seller_product(request)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
