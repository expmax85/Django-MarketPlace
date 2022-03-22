from decimal import Decimal
from typing import Union
from django.shortcuts import get_object_or_404
from orders_app.models import Order, OrderProduct
from orders_app.anonimcart import AnonymCart
from stores_app.models import SellerProduct


class CartService:
    """
    Сервис корзины

    add_to_cart: метод добавления товара в корзину
    increase_in_cart: увеличивает количество конкретной позиции в заказе на 1
    decrease_in_cart: уменьшает количество конкретной позиции в заказе на 1
    remove_from_cart: убирает товар из корзины
    change_quantity: изменяет количество товара в корзине
    get_goods: получение товаров из корзины
    get_quantity: получение количества товаров в корзине
    get_total_sum: получение общей суммы товаров в корзине
    get_total_discounted_sum: получение общей суммы товаров в корзине со скидками
    clear: очистка корзины
    """
    def __init__(self, request):
        if request.user.is_authenticated:
            self.cart, _ = Order.objects.get_or_create(defaults={'customer': request.user},
                                                       customer=request.user,
                                                       in_order=False)

        else:
            self.cart = AnonymCart(request)

    def add_to_cart(self, product_id: int, update_quantity=False) -> None:
        """
        добавить товар в корзину

        product: инстанс модели товара
        quantity: желаемое количество товаров
        """
        product = get_object_or_404(SellerProduct, id=product_id)
        if isinstance(self.cart, Order):
            cart_products = self.cart.order_products.select_related('seller_product')

            for cart_product in cart_products:
                if product.id == cart_product.seller_product.id:
                    if update_quantity:
                        cart_product.quantity = 1
                    else:
                        cart_product.quantity += 1
                    cart_product.save()
                    self.cart.save()
                    break
            else:
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

    def change_quantity(self, product, quantity: int, update_quantity=False) -> None:
        """
        изменить количество товара в корзине

        quantity: новое количество
        """
        if isinstance(self.cart, Order):
            # TODO Доработать
            try:
                cart_products = OrderProduct.objects.filter(order=self.cart, seller_product=product).all()
                cart_product = cart_products[0]
                if update_quantity:
                    cart_product.quantity = quantity
                else:
                    cart_product.quantity += quantity
            except IndexError:
                cart_product = OrderProduct(order=self.cart,
                                            seller_product=product,
                                            quantity=quantity,
                                            final_price=product.price_after_discount)
            cart_product.save()
            self.cart.save()
        else:
            self.cart.add(product, quantity, update_quantity=update_quantity)

    def update_product(self, product: SellerProduct, quantity: int, product_id: int) -> None:
        """
        изменить количество товара в корзине и заменить продавца

        quantity: новое количество
        """

        self.change_quantity(product, quantity)
        self.remove_from_cart(product_id)

    def get_goods(self) -> Union[OrderProduct, AnonymCart]:
        """получить товары из корзины"""
        if isinstance(self.cart, Order):
            return self.cart.order_products.all()
        return self.cart

    def get_quantity(self) -> int:
        """получить количество товаров в корзине"""
        return len(self.cart)

    def get_total_sum(self) -> Decimal:
        """получить общую сумму заказа"""
        if isinstance(self.cart, Order):
            return self.cart.total_sum
        return self.cart.total_sum()

    def get_total_discounted_sum(self) -> Decimal:
        """получить общую сумму заказа со скидками"""
        if isinstance(self.cart, Order):
            return self.cart.total_discounted_sum
        return self.cart.total_discounted_sum()

    def merge_carts(self, other):
        """Перенос анонимной корзины в корзину зарешистрированного"""
        for item in other.get_goods():
            self.change_quantity(item['seller_product'], item['quantity'])
        other.clear()

    def clear(self) -> None:
        """очистить корзину"""
        return self.cart.clear()

    def __len__(self):
        """получить общее количество товаров в корзине"""
        return len(self.cart)
