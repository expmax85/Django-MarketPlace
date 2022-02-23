import json
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpRequest
from orders_app.models import SellerProduct
from orders_app.utils import DecimalEncoder


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


class CompareView(View):
    """ Представление страницы товаров для сравнения """

    def get(self, request: HttpRequest):
        """ Данный метод рендерит страницу товаров для сравнения """

        #Эта часть кода является заглушкой, ввиду того что пока нет возможности
        #Сделать добавление в список для сранения, в сессию добавляются первые 4 товара из БД
        #На основе этого(примерно) можно реализовать сервис добавления в список для сравнения
        compared = dict()
        for product in list(SellerProduct.objects.all().select_related('product')[:4]):
            specifications = ({spec.current_specification.name: spec.value for spec in
                              product.product.specifications.all()})
            compared[product.product.name] = [product.price, product.price_after_discount, product.product.rating,
                                              specifications]
        #Далее уже то что будет в get методе
        request.session['compared'] = json.dumps(compared, cls=DecimalEncoder)
        context = self.create_queryset(session_data=request.session['compared'])
        return render(request, 'orders_app/compare.html', context)

    def create_queryset(self, session_data: json) -> dict[str, any]:
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