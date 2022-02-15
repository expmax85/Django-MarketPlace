from typing import Callable, Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from stores_app.forms import AddStoreForm, EditStoreForm
from stores_app.models import Seller
from stores_app.services import add_store, get_user_stores, get_store, edit_store


class SellersRoomView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Page for view seller room for Sellers-group"""
    permission_required = ('profiles_app.Sellers',)
    model = Seller
    template_name = 'stores_app/sellers_room.html'
    context_object_name = 'stores'

    def get_queryset(self) -> 'QuerySet':
        return get_user_stores(user=self.request.user)


class AddNewStoreView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Page for create new store"""
    permission_required = ('profiles_app.Sellers',)

    def get(self, request) -> Callable:
        form = AddStoreForm()
        return render(request, 'stores_app/add_store.html', context={'form': form})

    def post(self, request) -> Callable:
        form = AddStoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            add_store(user=request.user, form=form)
            return redirect(reverse('stores-polls:sellers-room'))
        form = AddStoreForm()
        return render(request, 'stores_app/add_store.html', context={'form': form})


class StoreDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Page for view and edit detail store"""
    permission_required = ('profiles_app.Sellers',)
    context_object_name = 'store'
    template_name = 'stores_app/store_detail.html'
    model = Seller
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None) -> QuerySet:
        return get_store(slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data()
        context['form'] = EditStoreForm(instance=self.get_object())
        return context

    def post(self, request, slug) -> Callable:
        form = EditStoreForm(request.POST, request.FILES)
        if form.is_valid():
            edit_store(store_slug=slug, form=form)
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:store_detail', kwargs={'slug': slug}))
