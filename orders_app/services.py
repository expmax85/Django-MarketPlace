from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from orders_app.models import Order, OrderProduct
from goods_app.models import Product
from orders_app.anonimcart import AnonymCart
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
    def __init__(self, request):
        if request.user.is_authenticated:
            self.cart, _ = Order.objects.get_or_create(defaults={'customer': request.user},
                                                       customer=request.user,
                                                       in_order=False)
        else:
            self.cart = AnonymCart(request)

    def add_to_cart(self, product_id: int) -> None:
        """
        добавить товар в корзину

        product: инстанс модели товара
        quantity: желаемое количество товаров
        """
        product = get_object_or_404(SellerProduct, id=product_id)
        if isinstance(self.cart, Order):
            OrderProduct.objects.create(order=self.cart,
                                        seller_product=product,
                                        quantity=1,
                                        final_price=product.price_after_discount)
        else:
            self.cart.add(product)

    def increase_in_cart(self, product_id: int) -> None:
        """
        увеличить количество товара в корзине
        product_id
        """
        product = get_object_or_404(SellerProduct, id=product_id)
        if isinstance(self.cart, Order):
            cart_product = get_object_or_404(OrderProduct, order=self.cart, seller_product=product)
            cart_product.quantity += 1
            cart_product.save()
            self.cart.save()
        else:
            self.cart.increase(product)

    def decrease_in_cart(self, product_id: int) -> None:
        """
        уменьшить количество товара в корзине
        product_id
        """
        product = get_object_or_404(SellerProduct, id=product_id)
        if isinstance(self.cart, Order):
            cart_product = get_object_or_404(OrderProduct, order=self.cart, seller_product=product)
            quantity = cart_product.quantity
            if quantity > 1:
                cart_product.quantity -= 1
                cart_product.save()
                self.cart.save()
        else:
            self.cart.decrease(product)

    def remove_from_cart(self, product_id: int) -> None:
        """
        убрать товар из корзины

        product_id: id товара
        """
        product = get_object_or_404(SellerProduct, id=product_id)
        if isinstance(self.cart, Order):
            cart_product = get_object_or_404(OrderProduct, order=self.cart, seller_product=product)
            cart_product.delete()
            self.cart.save()
        else:
            self.cart.remove(product)

    @classmethod
    def change_quantity(cls, request: HttpRequest, quantity: int) -> None:
        """
        изменить количество товара в корзине

        quantity: новое количество
        """

        pass

    def get_goods(self):
        """получить товары из корзины"""
        if isinstance(self.cart, Order):
            return self.cart.order_products.all()
        return self.cart

    def get_quantity(self) -> int:
        """получить количество товаров в корзине"""
        return len(self.cart)

    def get_total_sum(self):
        if isinstance(self.cart, Order):
            return self.cart.total_sum
        return self.cart.total_sum()

    def get_total_discounted_sum(self):
        if isinstance(self.cart, Order):
            return self.cart.total_discounted_sum
        return self.cart.total_discounted_sum()

    # def merge_to_logined(self, products):
    #     for product in products:
    #         if product in self.get_goods():
    #             print('Wow')
    #         else:
    #             product_id = product['seller_product'].id
    #             quantity = product['quantity']
    #             product = get_object_or_404(SellerProduct, id=product_id)
    #             OrderProduct.objects.create(order=self.cart,
    #                                         seller_product=product,
    #                                         quantity=quantity,
    #                                         final_price=product.price_after_discount)

    def clear(self):
        return self.cart.clear()

    def __len__(self):
        return len(self.cart)


class ViewedGoodsService:
    """
    Сервис просмотренных товаров

    add_to_list: добавляет товар в список сравнения
    add_to_cart: добавляет товар в корзину
    """

    @classmethod
    def add_to_list(cls, request: HttpRequest) -> None:
        """добавить товар в список сравнения"""

        pass

    @classmethod
    def add_to_cart(cls, request: HttpRequest, product: Product) -> None:
        """добавить товар в корзину"""

        pass