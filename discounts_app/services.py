import decimal
from datetime import date
from decimal import Decimal


class DiscountsService:
    """
    Сервис расчета скидок

    get_all_discounts_for_products: метод получения всех скидок на список товаров
    get_all_discounts_for_product: метод получения всех скидок на список товаров
    get_priority_discounts_for_products: метод получения приоритетных скидок на список товаров
    get_priority_discounts_for_product: метод получения приоритетных скидок на список товаров
    get_discounted_price: получение цены товарова с учетом скидки
    """

    def __init__(self, cart):
        self.cart = cart
        self.discounts = self.get_priority_discounts_for_products()

    def get_all_discounts_for_products(self) -> set:
        """
        Получить все скидки на список товаров

        discounts: список иснтансов скидок
        """
        discounts = []
        products = self.cart.get_goods()
        for product in products:
            discounts += self.get_all_discounts_for_product(product)

        return set(discounts)

    def get_priority_discounts_for_products(self) -> list:
        """
        Получить приоритетные скидки на список товаров

        discounts: список иснтансов скидок
        """
        priority_discounts = []
        discounts = self.get_all_discounts_for_products()
        for discount in discounts:
            class_name = discount.__class__.__name__
            if class_name == 'CartDiscount':
                if self.check_cart_discount(discount):
                    priority_discounts.append(discount)
            elif class_name == 'ProductDiscount':
                if discount.set_discount:
                    if self.check_set_discount(discount):
                        priority_discounts.append(discount)
                else:
                    priority_discounts.append(discount)
            else:
                priority_discounts.append(discount)

        return priority_discounts

    @staticmethod
    def get_all_discounts_for_product(product):
        """
        Получить все скидки на товар

        discounts: список иснтансов скидок
        """
        discounts = []

        if product.__class__.__name__ == 'OrderProduct':
            discounts += product.seller_product.seller.cart_discounts.filter(valid_from=None,
                                                                             valid_to=None,
                                                                             is_active=True).all() | \
                         product.seller_product.seller.cart_discounts.filter(valid_from__lte=date.today(),
                                                                             valid_to__gte=date.today(),
                                                                             is_active=True).all()
            discounts += product.seller_product.product.category.group_discounts.filter(valid_from=None,
                                                                                        valid_to=None,
                                                                                        is_active=True).all() | \
                         product.seller_product.product.category.group_discounts.filter(valid_from__lte=date.today(),
                                                                                        valid_to__gte=date.today(),
                                                                                        is_active=True).all()
            discounts += product.seller_product.product_discounts.filter(valid_from=None,
                                                                         valid_to=None,
                                                                         is_active=True).all() | \
                         product.seller_product.product_discounts.filter(valid_from__lte=date.today(),
                                                                         valid_to__gte=date.today(),
                                                                         is_active=True).all()
        else:
            discounts += product['seller_product'].seller.cart_discounts.filter(valid_from=None,
                                                                                valid_to=None,
                                                                                is_active=True).all() | \
                         product['seller_product'].seller.cart_discounts.filter(valid_from__lte=date.today(),
                                                                                valid_to__gte=date.today(),
                                                                                is_active=True).all()
            discounts += product['seller_product'].product.category.group_discounts.filter(valid_from=None,
                                                                                           valid_to=None,
                                                                                           is_active=True).all() | \
                         product['seller_product'].product.category.group_discounts.filter(valid_from__lte=date.today(),
                                                                                           valid_to__gte=date.today(),
                                                                                           is_active=True).all()
            discounts += product['seller_product'].product_discounts.filter(valid_from=None,
                                                                            valid_to=None,
                                                                            is_active=True).all() | \
                         product['seller_product'].product_discounts.filter(valid_from__lte=date.today(),
                                                                            valid_to__gte=date.today(),
                                                                            is_active=True).all()

        return discounts

    def get_priority_discounts_for_product(self, product):
        """
        Получить приоритетные скидки на товар

        discounts: список иснтансов скидок
        """
        product_discounts = set(self.get_all_discounts_for_product(product))
        result_discounts = set(self.discounts) & product_discounts
        priority = 0

        for discount in result_discounts:
            discount_priority = int(discount.priority)
            if discount_priority > int(priority):
                priority = discount.priority

        result_discounts = [discount for discount in result_discounts if int(discount.priority) == int(priority)]
        return result_discounts

    def check_cart_discount(self, discount) -> bool:
        """
        Проверка применимости корзинной скидки для данной корзины
        """
        cart_products = self.cart.get_goods()
        if cart_products.__class__.__name__ == 'QuerySet':
            ids = []
            for product in cart_products:
                ids.append(product.seller_product.seller.id)
            length = len(set(ids))
        else:
            ids = []
            for product in cart_products:
                ids.append(product['seller_product'].seller.id)
            length = len(set(ids))

        if length > 1:
            return False
        if discount.min_quantity_threshold <= len(self.cart) <= discount.max_quantity_threshold:
            return True
        if discount.total_sum_min_threshold <= self.cart.get_total_sum() <= discount.total_sum_max_threshold:
            return True

        return False

    def check_set_discount(self, discount) -> bool:
        """
        Проверка применимости наборной скидки для данного набора
        """
        cart_products = self.cart.get_goods()
        if cart_products.__class__.__name__ == 'QuerySet':
            cart_products = [item.seller_product for item in cart_products]
        else:
            cart_products = [item['seller_product'] for item in cart_products]
        discount_set_products = [item for item in discount.seller_products.all()]
        if set(discount_set_products) & set(cart_products) == set(discount_set_products):
            return True
        return False

    def get_discounted_price_in_cart(self, product) -> Decimal:
        """
        Расчитать цену со скидкой, если товар в текущей корзине
        """
        prices = []
        product_discounts = self.get_priority_discounts_for_product(product)
        if product.__class__.__name__ == 'OrderProduct':
            price = product.seller_product.price
        else:
            price = product['seller_product'].price

        if product_discounts:
            for discount in product_discounts:
                if discount.__class__.__name__ == 'CartDiscount':
                    cart_sum = self.cart.get_total_sum()
                    discounted_price = implement_discount(price, discount, cart_sum)
                else:
                    discounted_price = implement_discount(price, discount)
                prices.append(discounted_price)

        if prices:
            price = max(prices)

        if price < 1:
            price = 1

        return Decimal(round(price, 2))

    def get_discounted_price(self, product):
        """
        расчитать цену со скидкой
        """
        return self.get_discounted_price_in_cart(product)


def implement_discount(price: decimal, discount, cart_sum=None):
    """Функция расчета цены со скидкой"""
    if discount.__class__.__name__ == 'ProductDiscount' and \
            discount.set_discount is True or cart_sum:

        if discount.type_of_discount == 'f':
            if cart_sum:
                set_sum = cart_sum
            else:
                set_sum = sum([item.price for item in discount.seller_products.all()])
            set_sum_with_discount = set_sum - Decimal(discount.amount)
            price = Decimal(price * set_sum_with_discount / set_sum)
        elif discount.type_of_discount == 'p':
            price *= Decimal((100 - discount.percent) / 100)
        else:
            price = Decimal(discount.fixed_price)

    elif discount.type_of_discount == 'f':
        price -= Decimal(discount.amount)
    elif discount.type_of_discount == 'p':
        price *= Decimal((100 - discount.percent) / 100)
    else:
        price = Decimal(discount.fixed_price)

    return Decimal(round(price, 2))


def get_discounted_prices_for_seller_products(products: list, default_discount=None) -> zip:
    """
    Функция расчета цен со скидкой для тоавров продавцов, отображаемых на различных страницах сайта.
    Принимает на вход спискок товаров в магазине SellerProducts и необязательный аргумент - дефолтную скидку.
    Возвращает zip из кортежей (SellerProduct, цена со скидкой, сама скидка)
    """
    discounted_prices = []
    discounts = []

    for product in products:
        price = product.price
        if default_discount is None:
            discount = product.product_discounts.filter(
                is_active=True,
                set_discount=False
            ).order_by('-priority').first()
        else:
            discount = default_discount

        if not discount:
            discounted_prices.append(None)
            discounts.append(None)
        else:
            price = implement_discount(price, discount)

            if price < 1:
                price = 1
            discounted_prices.append(Decimal(price))
            discounts.append(discount)
    products = zip(products, discounted_prices, discounts)
    return products
