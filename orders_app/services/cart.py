from decimal import Decimal
from typing import Union
from django.shortcuts import get_object_or_404
from orders_app.models import Order, OrderProduct
from orders_app.services.anonim_cart import AnonymCart
from stores_app.models import SellerProduct
from orders_app.utils import check_stock


class CartService:
    """
    Сервис корзины

    add_to_cart: метод добавления товара в корзину
    remove_from_cart: убирает товар из корзины
    update_product: изменить количество товара в корзине и заменить продавца
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

    def remove_from_cart(self, product_id: int) -> None:
        """
        убрать товар из корзины

        product_id: id товара
        """
        product = get_object_or_404(SellerProduct, id=product_id)
        if isinstance(self.cart, Order):
            cart_product = get_object_or_404(OrderProduct, order=self.cart, seller_product=product)
            product.quantity += cart_product.quantity
            product.save()
            cart_product.delete()
            self.cart.save()
        else:
            self.cart.remove(product)

    def add_to_cart(self, product, quantity: int, price: Decimal = 0, update_quantity=False) -> bool:
        """
        изменить количество товара в корзине

        quantity: новое количество
        """
        if isinstance(self.cart, Order):
            cart_product = OrderProduct.objects.filter(order=self.cart, seller_product=product).first()
            if not cart_product:
                cart_product = OrderProduct(order=self.cart,
                                            seller_product=product,
                                            quantity=0,
                                            final_price=price)

            if update_quantity:
                delta = quantity - cart_product.quantity
                if check_stock(product, delta):
                    cart_product.quantity = quantity
                    cart_product.save()
                    self.cart.save()
                    return True

                return False

            else:
                delta = quantity
                if check_stock(product, delta):
                    cart_product.quantity += quantity
                    cart_product.save()
                    self.cart.save()
                    return True

                return False
        else:
            return self.cart.add(product, quantity, update_quantity=update_quantity)

    def update_product(self, product: SellerProduct, quantity: int, product_id: int) -> None:
        """
        изменить количество товара в корзине и заменить продавца

        quantity: новое количество
        """
        if self.add_to_cart(product, quantity):
            self.remove_from_cart(product_id)

    def get_goods(self) -> Union[OrderProduct, AnonymCart]:
        """получить товары из корзины"""
        if isinstance(self.cart, Order):
            return self.cart.order_products.prefetch_related('seller_product__product_discounts').all()
        return self.cart

    def get_quantity(self) -> int:
        """получить количество товаров в корзине"""
        return len(self.cart)

    def get_total_sum(self) -> Decimal:
        """получить общую сумму заказа"""
        if isinstance(self.cart, Order):
            return self.cart.total_sum
        return self.cart.total_sum()

    def merge_carts(self, other):
        """Перенос анонимной корзины в корзину зарегистрированного"""
        for item in other.get_goods():
            self.add_to_cart(item['seller_product'], item['quantity'],)
        other.clear()

    def clear(self) -> None:
        """очистить корзину"""
        return self.cart.clear()

    def save(self) -> None:
        """Сохранить корзину (любую сущность)"""
        return self.save()

    def __len__(self):
        """получить общее количество товаров в корзине"""
        return len(self.cart)
