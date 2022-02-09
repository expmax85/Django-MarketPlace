from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpRequest
from orders_app.services import CartService, ViewedGoodsService
from profiles_app.models import ViewedProduct


class CartView(View):
    """ Представление корзины """

    def get(self, request: HttpRequest):
        """ Данный метод пока только рендерит страницу корзины """

        return render(request, 'orders_app/cart.html')

    def post(self, request: HttpRequest):
        """ Здесь будет происходить добавление/обновление/удаление товаров """

        pass


class ViewedGoodsView(ListView):
    """ Представление просмотренных товаров """

    def get(self, request: HttpRequest, **kwargs):
        """ Данный метод пока только рендерит страницу просмотренных товаров """

        return render(request, 'orders_app/historyview.html')



