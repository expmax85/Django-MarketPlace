import json
from typing import Dict

import braintree
from django.contrib.messages.storage import session
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpRequest
from orders_app.models import Order, CompareProductStorage
from orders_app.forms import OrderStepOneForm, OrderStepTwoForm, OrderStepThreeForm
from orders_app.services import CartService
from orders_app.utils import DecimalEncoder
from stores_app.models import SellerProduct


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

        items = cart.get_goods()

        total = cart.get_quantity
        total_price = cart.get_total_sum
        total_discounted_price = cart.get_total_discounted_sum

        context = {'items': items,
                   'total': total,
                   'total_price': total_price,
                   'total_discounted_price': total_discounted_price}

        return render(request, 'orders_app/cart.html', context=context)

    def post(self, request: HttpRequest, product_id):
        """ Здесь будет происходить добавление/обновление/удаление товаров """
        cart = CartService(request)
        product = get_object_or_404(SellerProduct, id=str(request.POST['option']))
        quantity = int(request.POST['amount'])

        if quantity < 1:
            quantity = 1
        if int(product_id) == product.id:
            cart.change_quantity(product, quantity, True)
        else:
            cart.update_product(product, quantity, product_id)

        return redirect('orders:cart_detail')


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
    form_class = OrderStepOneForm
    template_name = 'orders_app/order_step_one.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        initial = {'fio': f'{user.first_name} {user.last_name}',
                   'email': user.email,
                   'phone': user.phone,
                   'delivery': 'exp',
                   'payment': 'cash'}
        form = self.form_class(initial=initial)

        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
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

        return render(request, self.template_name, {'form': form})


class OrderStepTwo(View):
    """Представление второго шага оформления заказа"""
    form_class = OrderStepTwoForm
    template_name = 'orders_app/order_step_two.html'

    def get(self, request: HttpRequest):
        user = request.user
        initial = {'city': user.city,
                   'address': user.address,
                   'delivery': 'exp',
                   'payment': 'cash'}
        form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

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
            order.save()

            return redirect('orders:order_step_three')
        return render(request, self.template_name, {'form': form})


class OrderStepThree(View):
    """Представление третьего шага оформления заказа"""
    form_class = OrderStepThreeForm
    template_name = 'orders_app/order_step_three.html'

    def get(self, request: HttpRequest):
        form = OrderStepThreeForm
        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            order.payment_method = payment_method
            order.in_order = True
            order.save()
            return redirect('orders:order_step_four')

        return render(request, self.template_name, {'form': form})


class OrderStepFour(View):
    """Представление четвертого шага оформления заказа"""
    template_name = 'orders_app/order_step_four.html'

    def get(self, request: HttpRequest):
        order = Order.objects.filter(customer=request.user, in_order=True).last()
        return render(request, self.template_name, {'order': order})


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
        else:
            return redirect('orders:payment_with_account', order_id)


class PaymentWithCardView(View):
    """
    Представление оплаты банковской картой
    """
    template_name = 'orders_app/payment_card.html'

    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        client_token = braintree.ClientToken.generate()
        context = {'order': order, 'client_token': client_token}
        return render(request, self.template_name, context=context)

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


class PaymentWithAccountView(View):
    """
    Представление оплаты банковской картой
    """
    template_name = 'orders_app/payment_account.html'

    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        client_token = braintree.ClientToken.generate()
        context = {'order': order, 'client_token': client_token}
        return render(request, self.template_name, context=context)


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

        #Эта часть кода является заглушкой, ввиду того что пока нет возможности
        #Сделать добавление в список для сранения, в сессию добавляются первые 4 товара из БД
        #На основе этого(примерно) можно реализовать сервис добавления в список для сравнения
        compared = dict()
        # for product in list(SellerProduct.objects.all())[:4]:
        for product in list(SellerProduct.objects.filter(compare_storage__user=request.user)):
            specifications = ({spec.current_specification.name: spec.value for spec in
                              product.product.specifications.all()})
            image = product.product.image.url if product.product.image else None
            compared[product.product.name] = [product.price, product.price_after_discount, product.product.rating,
                                              specifications, image]
        #Далее уже то что будет в get методе
        request.session['compared'] = json.dumps(compared, cls=DecimalEncoder)
        context = self.create_queryset(session_data=request.session['compared'])
        return render(request, 'orders_app/compare.html', context)

    def create_queryset(self, session_data: json) -> Dict:
        """ Здесь формируется queryset для сравнения товаров """

        # Здесь достаем товары для сравнения из сессии
        compared = json.loads(session_data)
        # Здесь для удобства отдельный словарь по характеристикам
        specifications = {key: list() for spec in compared.values() for key in spec[3].keys()}
        incoming_specifications = [value[3] for value in compared.values()]
        for item in incoming_specifications:
            for name in specifications.keys():
                if name in item.keys():
                    specifications[name].append(item[name])
                else:
                    specifications[name].append('no data')
        #Здесь проверка на одинаковые характеристики
        for value in specifications.values():
            if len(value) == value.count(value[0]):
                value.append(True)
        return {'compared': compared, 'specifications': specifications}


def add_to_compare(request, product_id):
    compare, created = CompareProductStorage.objects.get_or_create(product_id=product_id, user=request.user)
    # if created:
    #     compare.delete()
    return redirect(request.META.get('HTTP_REFERER'))
