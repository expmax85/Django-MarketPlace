from typing import Callable, Dict

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from profiles_app.services import reset_phone_format
from stores_app.forms import *
from stores_app.models import Seller
from stores_app.services import StoreServiceMixin


CREATE_SP_ERROR = 150


class SellersRoomView(LoginRequiredMixin, PermissionRequiredMixin, StoreServiceMixin, ListView):
    """   Page for view seller room for Sellers-group   """
    permission_required = ('profiles_app.Sellers',)
    model = Seller
    template_name = 'stores_app/sellers_room.html'
    context_object_name = 'stores'

    def get_queryset(self) -> 'QuerySet':
        return self.get_user_stores(user=self.request.user)

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['categories'] = self.get_categories()
        context['seller_products'] = self.get_seller_products(user=self.request.user)
        return context


class AddNewStoreView(LoginRequiredMixin, PermissionRequiredMixin, StoreServiceMixin, View):
    """   Page for creating new store   """
    permission_required = ('profiles_app.Sellers',)


    def get(self, request) -> Callable:
        form = AddStoreForm()
        return render(request, 'stores_app/add_store.html', context={'form': form})

    def post(self, request) -> Callable:
        form = AddStoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save()
            reset_phone_format(store)
            return redirect(reverse('stores-polls:sellers-room'))
        return render(request, 'stores_app/add_store.html', context={'form': form})


class EditStoreView(LoginRequiredMixin, PermissionRequiredMixin, StoreServiceMixin, DetailView):
    """   Page for view and edit detail store   """
    permission_required = ('profiles_app.Sellers',)
    context_object_name = 'store'
    template_name = 'stores_app/edit-store.html'
    model = Seller
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data()
        context['form'] = EditStoreForm(instance=self.get_object())
        return context

    def post(self, request, slug: str) -> Callable:
        form = EditStoreForm(request.POST, request.FILES, instance=self.get_object())
        if form.is_valid():
            store = form.save()
            reset_phone_format(store)
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-store', kwargs={'slug': slug}))


class StoreDetailView(StoreServiceMixin, DetailView):
    """   Page for Store Detail   """
    context_object_name = 'store'
    template_name = 'stores_app/store_detail.html'
    model = Seller
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['products'] = self.get_products(instance=self.get_object())
        return context


class AddSellerProductView(LoginRequiredMixin, PermissionRequiredMixin, StoreServiceMixin, View):
    """   Page for adding new seller product   """
    permission_required = ('profiles_app.Sellers',)

    def get_queryset(self, request) -> QuerySet:
        category_id = request.GET.get('category_id')
        return self.get_products(category_id=category_id)

    def get(self, request) -> Callable:
        context = dict()
        context['products'] = self.get_queryset(request)
        context['discounts'] = self.get_discounts()
        context['stores'] = self.get_user_stores(user=request.user)
        context['form'] = AddSellerProductForm()
        return render(request, 'stores_app/new_product_in_store.html', context=context)

    def post(self, request) -> Callable:
        form = AddSellerProductForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            created = self.create_seller_product(data=form.cleaned_data)
            if not created:
                messages.add_message(request, CREATE_SP_ERROR, _('This product is already exist in those store!'))
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return redirect(reverse('stores-polls:sellers-room'))
        return render(request, 'stores_app/new_product_in_store.html', {'form': form})


class EditSelleProductView(LoginRequiredMixin, PermissionRequiredMixin, StoreServiceMixin, DetailView):
    """    Page for editing SellerProduct instance    """
    permission_required = ('profiles_app.Sellers',)
    context_object_name = 'item'
    template_name = 'stores_app/edit-seller-product.html'
    model = SellerProduct
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data()
        context['form'] = EditSellerProductForm(instance=self.get_object())
        context['discounts'] = self.get_discounts()
        return context

    def post(self, request, slug: str, pk: int) -> Callable:
        form = EditSellerProductForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save(commit=False)
            self.edit_seller_product(data=form.cleaned_data, instance=self.get_object())
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-seller-product', kwargs={'slug': slug, 'pk': pk}))


@permission_required('profiles_app.Sellers')
def remove_Store(request) -> Callable:
    if request.method == 'GET':
        StoreServiceMixin.remove_store(request)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@permission_required('profiles_app.Sellers')
def remove_SellerProduct(request) -> Callable:
    if request.method == 'GET':
        StoreServiceMixin.remove_seller_product(request)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
