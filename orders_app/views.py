import json
import re
from typing import Dict, Callable
import braintree
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.http.response import Http404
from orders_app.models import (
    Order,
    ViewedProduct,
    OrderProduct
)

from orders_app.services.cart import CartService
from orders_app.forms import OrderStepOneForm, OrderStepTwoForm, OrderStepThreeForm
from orders_app.utils import DecimalEncoder
from profiles_app.forms import RegisterForm
from profiles_app.services import reset_phone_format, get_auth_user
from stores_app.models import SellerProduct
from discounts_app.services import DiscountsService, get_discounted_prices_for_seller_products
from settings_app.dynamic_preferences_registry import global_preferences_registry
from payments_app.services import process_payment
from stores_app.services import StoreServiceMixin

User = get_user_model()


def add_viewed(request):
    """
    Добавление в список просмотренных товаров

    ::Страница: Детальная страница товара
    """

    seller_product = SellerProduct.objects.get(id=request.GET.get('seller_product_id'))
    if request.user.is_anonymous:
        ViewedProduct.objects.get_or_create(session=request.session.session_key,
                                            product=seller_product)
    else:
        ViewedProduct.objects.get_or_create(user=request.user,
                                            product=seller_product)
    return redirect(reverse('goods-polls:product-detail', kwargs={'slug': seller_product.product.slug}))


def cart_clear(request):
    """
    Очистка корзины

    ::Страница: Корзина
    """
    cart = CartService(request)
    cart.clear()
    return redirect('orders:cart_detail')


class CartView(View):
    """
    Представление корзины

    ::Страница: Корзина
    """

    @classmethod
    def get(cls, request: HttpRequest):
        cart = CartService(request)
        discount_service = DiscountsService(cart)

        discounted_prices = []
        quantities = []

        items = cart.get_goods()
        for item in items:
            discounted_price = discount_service.get_discounted_price(item)

            if isinstance(item, OrderProduct):
                item.final_price = discounted_price
                item.save()
                quantities.append(item.quantity)
            else:
                item['final_price'] = discounted_price
                quantities.append(item['quantity'])

            discounted_prices.append(discounted_price)

        products = zip(items, discounted_prices)
        total = cart.get_quantity
        total_price = cart.get_total_sum
        total_discounted_price = sum([quantities[i] * discounted_prices[i] for i in range(len(items))])

        context = {'items': products,
                   'total': total,
                   'total_price': total_price,
                   'total_discounted_price': total_discounted_price
                   }

        return render(request, 'orders_app/cart.html', context=context)

    @classmethod
    def post(cls, request: HttpRequest, product_id):
        cart = CartService(request)

        product = get_object_or_404(SellerProduct, id=str(request.POST.get('option')))
        quantity = int(request.POST.get('amount'))

        if quantity < 1:
            quantity = 1
        if int(product_id) == product.id:
            cart.add_to_cart(product, quantity, update_quantity=True)
        else:
            cart.update_product(product, quantity, product_id)

        return redirect('orders:cart_detail')


class CartAdd(View):
    """
    Добавление позиций в корзине

    ::Страница: Корзина
    """
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        product = get_object_or_404(SellerProduct, id=str(product_id))
        cart.add_to_cart(product, quantity=1, update_quantity=False)
        return redirect(request.META.get('HTTP_REFERER'))

    def post(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        product = get_object_or_404(SellerProduct, id=str(product_id))
        quantity = int(request.POST.get('amount'))
        added = cart.add_to_cart(product, quantity=quantity, update_quantity=False)
        if added:
            messages.add_message(request, settings.SUCCESS_ADD_TO_CART, _(f'{product.product.name} was added to cart succesfully.'))
        else:
            messages.add_message(request, settings.ERROR_ADD_TO_CART, _(f'The quantity in stock for {product.product.name} is not enough.'))
        return redirect(request.META.get('HTTP_REFERER'))


class CartRemove(View):
    """
    Удаление позиции из корзины

    ::Страница: Корзина
    """
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        cart.remove_from_cart(product_id)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class OrderStepOne(View):
    """
    Представление первого шага оформления заказа

    ::Страница: Оформление заказа
    """
    form_class = OrderStepOneForm
    template_name = 'orders_app/order_step_one.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            initial = {'fio': f'{user.first_name} {user.last_name}',
                       'email': user.email,
                       'phone': user.phone,
                       'delivery': 'exp',
                       'payment': 'cash'}
        else:
            initial = {'delivery': 'exp',
                       'payment': 'cash'}

        form = self.form_class(initial=initial)

        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:
                order = Order.objects.get(customer=request.user, in_order=False)
                fio = form.cleaned_data['fio']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']

                order.fio = fio
                order.email = email
                order.phone = phone
                order.save()

                return redirect('orders:order_step_two')
            else:
                return redirect('profiles:login')

        return render(request, self.template_name, {'form': form})


class OrderStepOneAnonym(View):
    """
    Представление первого шага оформления заказа для анонимного пользователя

    ::Страница: Оформление заказа
    """
    def get(self, request: HttpRequest) -> Callable:
        if request.user.is_authenticated:
            return redirect('orders-polls:order_step_one')

        form = RegisterForm()

        context = {'form': form}
        return render(request, 'orders_app/order_step_one_anonimous.html', context=context)

    def post(self, request: HttpRequest) -> Callable:
        """
        Метод переопределен для слияние анонимной корзины
        с корзиной аутентифицированного пользователя
        """
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            old_cart = CartService(self.request)
            user = form.save()
            reset_phone_format(instance=user)
            login(request, get_auth_user(data=form.cleaned_data))
            new_cart = CartService(self.request)
            new_cart.merge_carts(old_cart)

            discount_service = DiscountsService(new_cart)
            items = new_cart.get_goods()
            for item in items:
                discounted_price = discount_service.get_discounted_price(item)
                item.final_price = discounted_price
                item.save()

            order = Order.objects.get(customer=request.user, in_order=False)
            fio = request.POST.get('name')
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            if fio:
                order.fio = fio
            order.email = email
            order.phone = phone
            order.save()
            return redirect('orders:order_step_two')

        return render(request, 'orders_app/order_step_one_anonimous.html', {'form': form})


class OrderStepTwo(View):
    """
    Представление второго шага оформления заказа

    ::Страница: Оформление заказа
    """
    form_class = OrderStepTwoForm
    template_name = 'orders_app/order_step_two.html'

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            initial = {'city': user.city,
                       'address': user.address,
                       'delivery': 'reg',
                       'payment': 'cash'}
            form = self.form_class(initial=initial)
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('profiles:login')

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            delivery = form.cleaned_data['delivery']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']

            order.delivery = delivery
            order.city = city
            order.address = address

            first_product = order.order_products.first()
            if first_product:
                global_preferences = global_preferences_registry.manager()

                if order.delivery == 'reg':
                    first_product_seller = first_product.seller_product.seller
                    same_store_products = order.order_products.filter(seller_product__seller=first_product_seller).count()
                    if same_store_products != len(order) or order.total_discounted_sum < 2000:
                        order.delivery_cost = global_preferences['general__regular_shipping']
                else:
                    order.delivery_cost = global_preferences['general__express_shipping']

            order.save()

            return redirect('orders:order_step_three')
        return render(request, self.template_name, {'form': form})


class OrderStepThree(View):
    """
    Представление третьего шага оформления заказа

    ::Страница: Оформление заказа
    """
    form_class = OrderStepThreeForm
    template_name = 'orders_app/order_step_three.html'

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            form = OrderStepThreeForm
            return render(request, self.template_name, {'form': form})

        else:
            return redirect('profiles:login')

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            order.payment_method = payment_method
            order.in_order = True
            order.ordered = datetime.datetime.today()
            order.save()
            return redirect('orders:order_step_four')

        return render(request, self.template_name, {'form': form})


class OrderStepFour(View):
    """
    Представление четвертого шага оформления заказа

    ::Страница: Оформление заказа
    """
    template_name = 'orders_app/order_step_four.html'

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            order = Order.objects.filter(customer=user, in_order=True).last()
            return render(request, self.template_name, {'order': order})

        else:
            return redirect('profiles:login')


class PaymentView(View):
    """
    Оплата заказа. Логика направляется в зависимости от способа оплаты.

    ::Страница: Оплата заказа
    """
    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.payment_method == 'card':
            return redirect('orders:payment_with_card', order_id)
        else:
            return redirect('orders:payment_with_account', order_id)


class PaymentWithCardView(View):
    """
    Представление оплаты банковской картой

    ::Страница: Оплата заказа
    """
    template_name = 'orders_app/payment_card.html'

    def get(self, request: HttpRequest, order_id: int):
        try:
            order = get_object_or_404(Order, id=order_id)
        except Http404:
            order = None
        client_token = braintree.ClientToken.generate()
        context = {'order': order, 'client_token': client_token}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        nonce = request.POST.get('payment_method_nonce', None)
        # Создание и сохранение транзакции.
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(order.final_total),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            order.paid = True
            order.braintree_id = result.transaction.id
            order.save()
            return render(request, 'orders_app/payment_process.html', {'result': True})
        order.payment_error = re.search(r"(?<=')(.*?)(?=')", str(result)).group()
        order.save()
        return render(request, 'orders_app/payment_process.html', {'result': False})


class PaymentWithAccountView(View):
    """
    Представление оплаты рандомным счетом

    ::Страница: Оплата заказа
    """
    template_name = 'orders_app/payment_account.html'

    def get(self, request: HttpRequest, order_id: int):
        order = get_object_or_404(Order, id=order_id)
        context = {'order': order}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, order_id: int):
        account = ''.join(request.POST.get('numero1').split(' '))
        result = process_payment(order_id, account)
        return render(request, 'orders_app/payment_process.html', {'result': result})


def payment_done(request):
    """
    Представление удачной оплаты

    ::Страница: Оплата заказа
    """
    return render(request, 'orders_app/payment_successful.html')


def payment_canceled(request):
    """
    Представление неудачной оплаты

    ::Страница: Оплата заказа
    """
    return render(request, 'orders_app/payment_unsuccessful.html')


class ViewedGoodsView(StoreServiceMixin, ListView):
    """
    Представление просмотренных товаров

    ::Страница: История просмотренных товаров
    """

    model = User
    context_object_name = 'goods'
    template_name = 'orders_app/historyview.html'

    def get_queryset(self):
        """ Получить просмотренные товары """

        if self.request.user.is_authenticated:
            products_in_session = ViewedProduct.objects.filter(session=self.request.session.session_key).all()
            for obj in products_in_session:
                ViewedProduct.objects.get_or_create(user=self.request.user,
                                                    product=obj.product)
        queryset = self.get_viewed_products(user=self.request.user)[20::-1]
        products = get_discounted_prices_for_seller_products(queryset)
        return products


class CompareView(View):
    """
    Представление страницы товаров для сравнения

    ::Страница: Сравнение товаров
    """

    def get(self, request: HttpRequest):
        """ Данный метод рендерит страницу товаров для сравнения """

        try:
            context = self.create_queryset(session_data=request.session['compared'])
        except KeyError:
            context = dict()
        return render(request, 'orders_app/compare.html', context)

    @classmethod
    def create_queryset(cls, session_data: json) -> Dict:
        """ Здесь формируется queryset для сравнения товаров """

        compared = json.loads(session_data)
        specifications = {key: list() for spec in compared.values() for key in spec[3].keys()}
        incoming_specifications = [value[3] for value in compared.values()]
        for item in incoming_specifications:
            for name in specifications.keys():
                if name in item.keys():
                    specifications[name].append(item[name])
                else:
                    specifications[name].append(_('no data'))
        for value in specifications.values():
            if len(value) == value.count(value[0]):
                value.append(True)
        equal_categories = cls.check_equal_categories(compared)
        return {'compared': compared, 'specifications': specifications, 'is_equals': equal_categories}

    @classmethod
    def check_equal_categories(cls, compared):
        """ Проверяет есть ли товары одинаковой категории """

        categories = list()
        for item in compared. values():
            categories.append(item[6])
        return len(set(categories)) == 1

    @classmethod
    def get_quantity(cls, request):
        """ Данный метод возвращает количество товаров в списке для сравнения """

        try:
            compared = json.loads(request.session['compared'])
            return len(list(compared.keys()))
        except KeyError:
            return 0


class AddToCompare(View):
    """
    Представление добавления товара в список для сравнения

    ::Страница: Сравнение товаров
    """

    def get(self, request: HttpRequest, product_id: int):
        """ Вызывает метод добавления товара для сравнения и возвращает на исходный url """

        self.add_to_compare(request, product_id)
        return redirect(request.META.get('HTTP_REFERER'))

    @classmethod
    def add_to_compare(cls, request: HttpRequest, product_id: int) -> None:
        """ Данный метод добавляет товар в список для сравнения """

        product = SellerProduct.objects.get(id=product_id)
        if 'compared' in request.session.keys():
            compared = json.loads(request.session['compared'])
            if len(compared.keys()) == 4:
                compared.pop(list(compared.keys())[0])
        else:
            compared = dict()
        specifications = ({spec.current_specification.name: spec.value for spec in
                           product.product.specifications.all()})
        image = product.product.image_url
        price_after_discount = product.price
        category = product.product.category.name
        for item in get_discounted_prices_for_seller_products([product]):
            product = item[0]
            if item[1]:
                price_after_discount = item[1]
        compared[product.product.name] = [product.price, price_after_discount,
                                          product.product.rating, specifications,
                                          image, int(product.id),
                                          category]
        request.session['compared'] = json.dumps(compared, cls=DecimalEncoder)


class RemoveFromCompare(View):
    """
    Представление удаления товара из списка товаров для сравнения

    ::Страница: Сравнение товаров
    """

    def get(self, request: HttpRequest, product_name: str):
        """ Удаляет товар из сравниваемых товаров по ключу и возвращает на исходный url"""

        compared = json.loads(request.session['compared'])
        compared.pop(product_name)
        request.session['compared'] = json.dumps(compared, cls=DecimalEncoder)
        return redirect(request.META.get('HTTP_REFERER'))


class HistoryOrderView(StoreServiceMixin, ListView):
    """
    Представление истории заказов

    ::Страница: История заказов
    """

    model = Order
    context_object_name = 'orders'
    template_name = 'orders_app/historyorder.html'

    def get_queryset(self):
        """ Получить заказы """

        queryset = self.get_all_orders(user=self.request.user).order_by('-ordered',)
        return queryset


class HistoryOrderDetail(DetailView):
    """
    Детальное представление заказа

    ::Страница: Детальная страница заказа
    """

    model = Order

    def get(self, request, *args, **kwargs):
        """ Получить заказ """

        pk = kwargs['order_id']
        order = self.model.objects.prefetch_related('order_products').get(id=pk)
        return render(request, 'orders_app/oneorder.html', context={'order': order})
