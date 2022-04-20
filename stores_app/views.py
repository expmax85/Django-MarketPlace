from typing import Callable, Dict

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpRequest
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.core.management import call_command

from django.conf import settings
from discounts_app.models import ProductDiscount, GroupDiscount, CartDiscount
from stores_app.services import StoreServiceMixin
from goods_app.services.catalog import get_categories
from profiles_app.services import reset_phone_format
from stores_app.forms import AddStoreForm, EditStoreForm, \
    AddSellerProductForm, EditSellerProductForm, AddRequestNewProduct, ImportForm
from discounts_app.forms import AddProductDiscountForm, AddGroupDiscountForm, AddCartDiscountForm
from django.forms import ModelChoiceField
from stores_app.models import Seller, SellerProduct, ProductImportFile, ImportOrder
from stores_app.tasks import start_import


class StoreAppMixin(LoginRequiredMixin, PermissionRequiredMixin, StoreServiceMixin):
    permission_required = ('profiles_app.Sellers',)


class SellersRoomView(StoreAppMixin, ListView):
    """
    Страница раздела для продавцов на странице информации об аккаунте

    ::Страница: Аккаунт продавцов
    """
    model = Seller
    template_name = 'stores_app/sellers_room.html'
    context_object_name = 'stores'

    def get_queryset(self) -> 'QuerySet':
        return self.get_user_stores(user=self.request.user)

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        products = self.get_all_owner_products(user=self.request.user)
        context['seller_products'] = list(products)[:3]
        context['product_discounts'] = self.get_product_discounts(user=self.request.user)
        context['group_discounts'] = self.get_group_discounts(user=self.request.user)
        context['cart_discounts'] = self.get_cart_discounts(user=self.request.user)
        return context


class AddNewStoreView(StoreAppMixin, View):
    """
    Страница создания магазина

    ::Страница: Добавление магазина
    """

    def get(self, request: HttpRequest) -> Callable:
        form = AddStoreForm()
        return render(request, 'stores_app/add_store.html', context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
        form = AddStoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save()
            reset_phone_format(store)
            return redirect(reverse('stores-polls:sellers-room'))
        return render(request, 'stores_app/add_store.html', context={'form': form})


class EditStoreView(StoreAppMixin, DetailView):
    """
    Редактирование информации о магазине

    ::Страница: Редактирование магазина
    """
    context_object_name = 'store'
    template_name = 'stores_app/edit-store.html'
    model = Seller
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data()
        context['form'] = EditStoreForm(instance=self.get_object())
        return context

    def post(self, request: HttpRequest, slug: str) -> Callable:
        form = EditStoreForm(request.POST, request.FILES, instance=self.get_object())
        if form.is_valid():
            store = form.save()
            reset_phone_format(store)
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-store', kwargs={'slug': slug}))


class StoresListView(StoreServiceMixin, ListView):
    """
    Страница со списком всех магазинов

    ::Страница: Список всех магазинов
    """
    model = Seller
    template_name = 'stores_app/stores_list.html'
    slug_url_kwarg = 'slug'
    paginate_by = 9

    def get_queryset(self):
        return self.get_all_stores()


class AllSellerProductView(StoreAppMixin, ListView):
    """
    Страница со списком всех товаров продавца

    ::Страница: Список всех товаров продавца
    """
    model = SellerProduct
    context_object_name = 'products'
    template_name = 'stores_app/all_products_list.html'
    paginate_by = 9

    def get_queryset(self):
        products = self.get_all_owner_products(user=self.request.user)
        return list(products)


class StoreDetailView(StoreServiceMixin, DetailView):
    """
    Детальная страница магазина

    ::Страница: Детальная страница магазина
    """
    permission_required = None
    context_object_name = 'store'
    template_name = 'stores_app/store_detail.html'
    model = Seller
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        seller = self.get_object()
        context['products'] = self.get_seller_products(seller=seller)
        return context


class AddSellerProductView(StoreAppMixin, View):
    """
    Страница добавления нового продукта продавца

    ::Страница: Добавление продукта продавца
    """

    def get(self, request: HttpRequest) -> Callable:
        context = dict()
        context['categories'] = get_categories()
        context['products'] = self.get_base_products()
        context['stores'] = self.get_user_stores(user=request.user)
        context['form'] = AddSellerProductForm()
        return render(request, 'stores_app/new_product_in_store.html', context=context)

    def post(self, request: HttpRequest) -> Callable:
        form = AddSellerProductForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            created = self.create_seller_product(data=form.cleaned_data)
            if not created:
                messages.add_message(request, settings.CREATE_PRODUCT_ERROR,
                                     _('This product is already exist in those store!'))
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return redirect(reverse('stores-polls:sellers-room'))
        return render(request, 'stores_app/new_product_in_store.html', {'form': form})


class CategoryFilter(StoreServiceMixin, ListView):
    """
    Представление для выборки продуктов по категориям при создании продукта продавца

    ::Страница: Добавление продукта продавца
    """

    def get_queryset(self) -> QuerySet:
        category_id = self.request.GET.get('category_id')
        return self.get_base_products(category_id=category_id).values("id", "name")

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        queryset = self.get_queryset()
        return JsonResponse({'products': list(queryset)}, safe=False)


class EditSelleProductView(StoreAppMixin, DetailView):
    """
    Страница редактирования продукта продавца

    ::Страница: Редактирование продукта продавца
    """
    context_object_name = 'item'
    template_name = 'stores_app/edit-seller-product.html'
    model = SellerProduct
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data()
        context['form'] = EditSellerProductForm(instance=self.get_object())
        return context

    def post(self, request: HttpRequest, slug: str, pk: int) -> Callable:
        form = EditSellerProductForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            self.edit_seller_product(data=form.cleaned_data, instance=self.get_object())
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-seller-product', kwargs={'slug': slug, 'pk': pk}))


@permission_required('profiles_app.Sellers')
def remove_Store(request: HttpRequest) -> Callable:
    """
    Удаление магазина продавца

    ::Страница: Аккаунт продавцов
    """
    StoreServiceMixin.remove_store(request)
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Sellers')
def remove_SellerProduct(request: HttpRequest) -> Callable:
    """
    Удаление продукта продавца

    ::Страница: Аккаунт продавцов
    """
    StoreServiceMixin.remove_seller_product(request)
    return redirect('stores-polls:sellers-room')


@permission_required('profiles_app.Sellers')
def remove_ProductDiscount(request: HttpRequest) -> Callable:
    """
    Удаление скидки на товар

    ::Страница: Аккаунт продавцов
    """
    if request.method == 'GET':
        StoreServiceMixin.remove_store_product_discount(request)
        return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Sellers')
def remove_GroupDiscount(request: HttpRequest) -> Callable:
    """
    Удаление скидки на группу товаров

    ::Страница: Аккаунт продавцов
    """
    if request.method == 'GET':
        StoreServiceMixin.remove_store_group_discount(request)
        return redirect(request.META.get('HTTP_REFERER'))


@permission_required('profiles_app.Sellers')
def remove_CartDiscount(request: HttpRequest) -> Callable:
    """
    Удаление корзинной скидки

    ::Страница: Аккаунт продавцов
    """
    if request.method == 'GET':
        StoreServiceMixin.remove_store_cart_discount(request)
        return redirect(request.META.get('HTTP_REFERER'))


class RequestNewProduct(StoreAppMixin, View):
    """
    Страница для запроса создания нового продукта

    ::Страница: Запрос на новый продукт
    """

    def get(self, request: HttpRequest) -> Callable:
        categories = get_categories()
        stores = self.get_user_stores(user=request.user)
        form = AddRequestNewProduct()
        return render(request, 'stores_app/request-add-new-product.html', context={'form': form,
                                                                                   'categories': categories,
                                                                                   'stores': stores})

    def post(self, request: HttpRequest) -> Callable:
        form = AddRequestNewProduct(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            print(form.cleaned_data)
            self.request_add_new_product(product=product, user=request.user)
            messages.add_message(request, settings.SEND_PRODUCT_REQUEST,
                                 _('Your request was sending. Wait the answer some before time to your email!'))
            return redirect(reverse('stores-polls:sellers-room'))
        categories = get_categories()
        stores = self.get_user_stores(user=request.user)
        return render(request, 'stores_app/request-add-new-product.html', context={'form': form,
                                                                                   'categories': categories,
                                                                                   'stores': stores})


class AddProductDiscountView(StoreAppMixin, View):
    """
    Страница создания скидки на продукт

    ::Страница: Добавление скидки на продукт
    """

    def get(self, request: HttpRequest) -> Callable:
        context = dict()
        context['categories'] = get_categories()
        context['products'] = self.get_base_products()
        context['stores'] = self.get_user_stores(user=request.user)
        form = AddProductDiscountForm()
        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))
        # form.fields['seller_products'] = ModelChoiceField(SellerProduct.objects.
        #                                                   filter(seller__in=Seller.objects.filter(owner=request.user)))

        context['form'] = form
        return render(request, 'stores_app/product_discount_in_store.html', context=context)

    def post(self, request: HttpRequest) -> Callable:
        form = AddProductDiscountForm(request.POST)

        if form.is_valid():
            form.save(commit=False)
            created = self.create_product_discount(data=form.cleaned_data)
            if not created:
                # messages.add_message(request, CREATE_PRODUCT_ERROR,
                # _('This product is already exist in those store!'))
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return redirect(reverse('stores-polls:sellers-room'))

        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))
        form.fields['seller_products'] = ModelChoiceField(SellerProduct.objects.
                                                          filter(seller__in=Seller.objects.filter(owner=request.user)))
        return render(request, 'stores_app/product_discount_in_store.html', {'form': form})


class EditProductDiscountView(StoreAppMixin, DetailView):
    """
    Страница редактирования скидки на продукт

    ::Страница: Редактирование скидки на продукт
    """
    context_object_name = 'item'
    template_name = 'stores_app/product_discount_in_store.html'
    model = ProductDiscount
    slug_url_kwarg = 'slug'

    def get(self, request: HttpRequest, *args, **kwargs) -> Callable:
        instance = self.get_object()
        form = AddProductDiscountForm(instance=instance)
        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))
        # form.fields['seller_products'] = ModelChoiceField(SellerProduct.objects.
        #                                                   filter(seller__in=Seller.objects.filter(owner=request.user)))
        context = {'form': form}
        return render(request, 'stores_app/product_discount_in_store.html', context=context)

    def post(self, request: HttpRequest, slug: str, pk: int) -> Callable:
        form = AddProductDiscountForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            self.edit_store_product_discount(data=form.cleaned_data, instance=self.get_object())
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-store-product-discount', kwargs={'slug': slug, 'pk': pk}))


class AddGroupDiscountView(StoreAppMixin, View):
    """
    Страница создания скидки на группу товаров

    ::Страница: Добавление скидки на группу товаров
    """

    def get(self, request: HttpRequest) -> Callable:
        context = dict()
        context['categories'] = get_categories()
        # context['products'] = self.get_base_products()
        context['stores'] = self.get_user_stores(user=request.user)
        form = AddGroupDiscountForm()
        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))

        context['form'] = form
        return render(request, 'stores_app/product_discount_in_store.html', context=context)

    def post(self, request: HttpRequest) -> Callable:
        form = AddGroupDiscountForm(request.POST)

        if form.is_valid():
            form.save(commit=False)
            created = self.create_group_discount(data=form.cleaned_data)
            if not created:
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return redirect(reverse('stores-polls:sellers-room'))

        return render(request, 'stores_app/product_discount_in_store.html', {'form': form})


class EditGroupDiscountView(StoreAppMixin, DetailView):
    """
    Страница редактирования скидки на группу товаров

    ::Страница: Редактирование скидки на группу товаров
    """
    context_object_name = 'item'
    template_name = 'stores_app/product_discount_in_store.html'
    model = GroupDiscount
    slug_url_kwarg = 'slug'

    def get(self, request: HttpRequest, *args, **kwargs) -> Callable:
        instance = self.get_object()
        form = AddGroupDiscountForm(instance=instance)
        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))
        context = {'form': form}
        return render(request, 'stores_app/product_discount_in_store.html', context=context)

    def post(self, request: HttpRequest, slug: str, pk: int) -> Callable:
        form = AddGroupDiscountForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            self.edit_store_group_discount(data=form.cleaned_data, instance=self.get_object())
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-store-group-discount', kwargs={'slug': slug, 'pk': pk}))


class AddCartDiscountView(StoreAppMixin, View):
    """
    Страница создания новой корзинной скидки

    ::Страница: Добавление корзинной скидки
    """

    def get(self, request: HttpRequest) -> Callable:
        context = dict()
        context['stores'] = self.get_user_stores(user=request.user)
        form = AddCartDiscountForm()
        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))

        context['form'] = form
        return render(request, 'stores_app/product_discount_in_store.html', context=context)

    def post(self, request: HttpRequest) -> Callable:
        form = AddCartDiscountForm(request.POST)

        if form.is_valid():
            form.save(commit=False)
            created = self.create_cart_discount(data=form.cleaned_data)
            if not created:
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return redirect(reverse('stores-polls:sellers-room'))

        return render(request, 'stores_app/product_discount_in_store.html', {'form': form})


class EditCartDiscountView(StoreAppMixin, DetailView):
    """
    Страница редактирования корзинной скидки

    ::Страница: Редактирование корзинной скидки
    """
    context_object_name = 'item'
    template_name = 'stores_app/product_discount_in_store.html'
    model = CartDiscount
    slug_url_kwarg = 'slug'

    def get(self, request: HttpRequest, *args, **kwargs) -> Callable:
        instance = self.get_object()
        form = AddCartDiscountForm(instance=instance)
        form.fields['seller'] = ModelChoiceField(Seller.objects.filter(owner=request.user))
        context = {'form': form}
        return render(request, 'stores_app/product_discount_in_store.html', context=context)

    def post(self, request: HttpRequest, slug: str, pk: int) -> Callable:
        form = AddCartDiscountForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            self.edit_store_cart_discount(data=form.cleaned_data, instance=self.get_object())
            return redirect(reverse('stores-polls:sellers-room'))
        return redirect(reverse('stores-polls:edit-store-cart-discount', kwargs={'slug': slug, 'pk': pk}))


class ImportView(StoreAppMixin, View):
    """
    Представление страницы проведения импорта

    ::Страница: Импорт товаров из файла
    """

    def get(self, request):
        return render(request, 'stores_app/import.html', {})

    def post(self, request):
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = ProductImportFile.objects.create(file=request.FILES['file'],
                                                    user=request.user)
            file.save()
            start_import.delay([file.filename(), request.user.email, file.id])
        return redirect(request.META.get('HTTP_REFERER'))
