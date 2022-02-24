import braintree
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpRequest, HttpResponse
from orders_app.models import Order
from orders_app.forms import CartAddProductForm, OrderStepOneForm, OrderStepTwoForm, OrderStepThreeForm
from orders_app.services import CartService


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
        print(form.errors)
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
        print(form.errors)
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
        print(form.errors)
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
