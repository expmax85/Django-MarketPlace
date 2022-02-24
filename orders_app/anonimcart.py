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

    def add(self, product, quantity=1, update_quantity=False):
        """Добавление товара в корзину или обновление его количества"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price),
                                     'discounted_price': str(product.price_after_discount)}
        # if update_quantity: Пока не удалять
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def increase(self, product):
        """Увеличение количества товара в корзине на 1"""
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += 1
        self.save()

    def decrease(self, product):
        """Умньшение количества товара в корзине на 1"""
        product_id = str(product.id)
        if product_id in self.cart and self.cart[product_id]['quantity'] > 1:
            self.cart[product_id]['quantity'] -= 1
        self.save()

    def save(self):
        # Отметка сессии как измененной
        self.session.modified = True

    def remove(self, product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        print('Trying removing')
        if product_id in self.cart:
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
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """Получение количества товаров в корзине"""
        return sum(item['quantity'] for item in self.cart.values())

    def total_sum(self):
        """Получение общей стоимости товаров в корзине"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def total_discounted_sum(self):
        """Получение общей стоимости товаров в корзине со скидкой"""
        return sum(
            Decimal(item['discounted_price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """Очистка корзины"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
