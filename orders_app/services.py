from django.http import HttpRequest

#from orders_app.models import Cart, CartProduct
#TODO модель корзины, модель просмотренных/товаров для сравнения
from goods_app.models import Product
from stores_app.models import SellerProduct


class CartService:
    """
    Сервис корзины

    add_to_cart: метод добавления товара в корзину
    remove_from_cart: убирает товар из корзины
    change_quantity: изменяет количество товара в корзине
    get_goods: получение товаров из корзины
    get_quantity: получение количества товаров в корзине
    """

    @classmethod
    def add_to_cart(cls, request: HttpRequest, product: Product, quantity: int) -> None:
        """
        добавить товар в корзину

        product: иснтанс модели товара
        quantity: желаемое количество товаров
        """

        pass

    @classmethod
    def remove_from_cart(cls, request: HttpRequest, product_id: int) -> None:
        """
        убрать товар из корзины

        product_id: id товара
        """

        pass

    @classmethod
    def change_quantity(cls, request: HttpRequest, quantity: int) -> None:
        """
        изменить количество товара в корзине

        quantity: новое количество
        """

        pass

    @classmethod
    def get_goods(cls, request: HttpRequest):
        """получить товары из корзины"""

        pass

    @classmethod
    def get_quantity(cls, request: HttpRequest) -> int:
        """получить количество товаров в корзине"""

        pass


class ViewedGoodsService:
    """
    Сервис добавления в список просмотренных товаров/ список товаров для сравнения?

    add_to_list: добавляет товар в список сравнения
    remove_from_list: убирает товар из списка
    get_list: отдает список товаров для сравнения
    get_quantity: отдает количество товаров в списке для сравнения
    """

    @classmethod
    def add_to_list(cls, request: HttpRequest) -> None:
        """добавить товар в список сравнения"""

        pass

    @classmethod
    def remove_from_list(cls, request: HttpRequest) -> None:
        """убрать товар из списка"""

        pass

    @classmethod
    def get_list(cls, request: HttpRequest, quantity: int = 3):
        """
        получить список товаров, добавленных к сравнению

        quantity: ограничение на количество
        """

        pass

    @classmethod
    def get_quantity(cls, request: HttpRequest) -> int:
        """ получить количество товаров в списке для сравнения """

        pass