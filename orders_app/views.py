import json
from typing import Dict

import braintree
from django.contrib.messages.storage import session
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpRequest
from orders_app.models import Order
from orders_app.forms import OrderStepOneForm, OrderStepTwoForm, OrderStepThreeForm
from orders_app.services import CartService
from orders_app.utils import DecimalEncoder
from stores_app.models import SellerProduct
from django.utils.translation import gettext_lazy as _


def cart_clear(request):
    """Очистка корзины"""
    cart = CartService(request)
    cart.clear()
    return redirect('orders:cart_detail')


class CartView(View):
    """Представление корзины"""

    @staticmethod
    def get(request: HttpRequest):
        """ Данный метод пока только рендерит страницу корзины """
        cart = CartService(request)

        items = cart.get_goods
        total = cart.get_quantity
        total_price = cart.get_total_sum
        total_discounted_price = cart.get_total_discounted_sum

        context = {'items': items,
                   'total': total,
                   'total_price': total_price,
                   'total_discounted_price': total_discounted_price}

        return render(request, 'orders_app/cart.html', context=context)

    def post(self, request: HttpRequest):
        """ Здесь будет происходить добавление/обновление/удаление товаров """

        pass


class CartAdd(View):
    """Добавление позиций в корзине"""
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        cart.add_to_cart(product_id)
        return redirect(request.META.get('HTTP_REFERER'))


class CartIncreaseQuantity(View):
    """Увеличение позиции в корзине"""
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        cart.increase_in_cart(product_id)
        return redirect(request.META.get('HTTP_REFERER'))


class CartDecreaseQuantity(View):
    """Уменьшение позиции в корзине"""
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        cart.decrease_in_cart(product_id)
        return redirect(request.META.get('HTTP_REFERER'))


class CartRemove(View):
    """Удаделение позиции из корзины"""
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        cart.remove_from_cart(product_id)
        return redirect(request.META.get('HTTP_REFERER'))


class OrderStepOne(View):
    """Представление первого шага оформления заказа"""
    def get(self, request: HttpRequest):
        user = request.user
        initial = {'fio': f'{user.first_name} {user.last_name}',
                   'email': user.email,
                   'phone': user.phone,
                   'delivery': 'exp',
                   'payment': 'cash'}

        form = OrderStepOneForm(initial=initial)
        return render(request, 'orders_app/order_step_one.html', {'form': form})

    def post(self, request: HttpRequest):
        form = OrderStepOneForm(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            fio = form.cleaned_data['fio']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            order.fio = fio
            order.email = email
            order.phone = phone
            order.save()
            return redirect('orders:order_step_two')
        return render(request, 'orders_app/order_step_one.html', {'form': form})


class OrderStepTwo(View):
    """Представление второго шага оформления заказа"""
    def get(self, request: HttpRequest):
        form = OrderStepTwoForm()
        return render(request, 'orders_app/order_step_two.html', {'form': form})

    def post(self, request: HttpRequest):
        form = OrderStepTwoForm(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            delivery = form.cleaned_data['delivery']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            order.delivery = delivery
            order.city = city
            order.address = address
            order.save()
            return redirect('orders:order_step_three')
        return render(request, 'orders_app/order_step_two.html', {'form': form})


class OrderStepThree(View):
    """Представление третьего шага оформления заказа"""
    def get(self, request: HttpRequest):
        form = OrderStepThreeForm()
        return render(request, 'orders_app/order_step_three.html', {'form': form})

    def post(self, request: HttpRequest):
        form = OrderStepThreeForm(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            order.payment_method = payment_method
            order.in_order = True
            order.save()
            return redirect('orders:order_step_four')
        return render(request, 'orders_app/order_step_three.html', {'form': form})


class OrderStepFour(View):
    """Представление четвертого шага оформления заказа"""
    def get(self, request: HttpRequest):
        order = Order.objects.filter(customer=request.user, in_order=True).last()
        return render(request, 'orders_app/order_step_four.html', {'order': order})


class PaymentView(View):
    """
    Оплата заказа. Логика направлеемя в зависимости от способа оплаты.
    Пока реализована оплата картой.
    Оплата рандомным счетом в разработке
    """
    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.payment_method == 'card':
            return redirect('orders:payment_with_card', order_id)


class PaymentWithCardView(View):
    """
    Представление оплаты банковской картой
    """
    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        client_token = braintree.ClientToken.generate()
        return render(request,
                      'orders_app/payment.html',
                      {'order': order,
                       'client_token': client_token})

    def post(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        nonce = request.POST.get('payment_method_nonce', None)
        # Создание и сохранение транзакции.
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(1500),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # Отметка заказа как оплаченного.
            order.paid = True
            # Сохранение ID транзакции в заказе.
            order.braintree_id = result.transaction.id
            order.save()
            return redirect('orders:payment_done')
        else:
            return redirect('orders:payment_canceled')


def payment_done(request):
    """Представление удачной оплаты"""
    return render(request, 'orders_app/payment_successful.html')


def payment_canceled(request):
    """Представление неудачной оплаты"""
    return render(request, 'orders_app/payment_unsuccessful.html')


class ViewedGoodsView(ListView):
    """ Представление просмотренных товаров """

    def get(self, request: HttpRequest, **kwargs):
        """ Данный метод пока только рендерит страницу просмотренных товаров """

        return render(request, 'orders_app/historyview.html')


class CompareView(View):
    """ Представление страницы товаров для сравнения """

    def get(self, request: HttpRequest):
        """ Данный метод рендерит страницу товаров для сравнения """

        context = self.create_queryset(session_data=request.session['compared'])
        return render(request, 'orders_app/compare.html', context)

    def create_queryset(self, session_data: json) -> Dict:
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
        return {'compared': compared, 'specifications': specifications}

    def get_quantity(self, request):
        """ Данный метод возвращает количество товаров в списке для сравнения """
        try:
            compared = json.loads(request.session['compared'])
        except KeyError:
            return 0
        return len(list(compared.keys()))


class AddToCompare(View):
    """ Представление добавления товара в список для сравнения """

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
        image = product.product.image.url if product.product.image else None
        compared[product.product.name] = [product.price, product.price_after_discount,
                                          product.product.rating, specifications,
                                          image, int(product.id)]
        request.session['compared'] = json.dumps(compared, cls=DecimalEncoder)


class RemoveFromCompare(View):
    """ Представление удаления товара из списка товаров для сравнения """

    def get(self, request: HttpRequest, product_name: str):
        """ Удаляет товар из сравниваемых товаров по ключу и возвращает на исходный url"""

        compared = json.loads(request.session['compared'])
        compared.pop(product_name)
        request.session['compared'] = json.dumps(compared, cls=DecimalEncoder)
        return redirect(request.META.get('HTTP_REFERER'))
