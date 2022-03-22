from decimal import Decimal
from django.conf import settings
from stores_app.models import SellerProduct


class AnonymCart:
    """
    Класс корзины анонимного пользователя
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: SellerProduct, quantity: int = 1, update_quantity: bool = False):
        """Добавление товара в корзину или обновление его количества"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def update_product_quantity(self, product_id: str, quantity: int, update_quantity: bool = False) -> None:
        # Обновление количества товара в корзине
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Отметка сессии как измененной
        self.session.modified = True

    def remove(self, product: SellerProduct):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            print('Removing anyway')
            product.quantity += self.cart[product_id]['quantity']
            product.save()
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Проходим по товарам корзины и получаем соответствующие объекты Product"""
        product_ids = self.cart.keys()
        # Получаем объекты модели Product и передаем их в корзину.
        products = SellerProduct.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['seller_product'] = product
        for item in cart.values():
            # item['price'] = Decimal(item['price'])
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """Получение количества товаров в корзине"""
        return len(self.cart.values())

    def total_sum(self):
        """Получение общей стоимости товаров в корзине"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """Очистка корзины"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
