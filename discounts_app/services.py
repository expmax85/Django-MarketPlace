from datetime import date
from typing import List
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

    def get_all_discounts_for_products(self):
        """
        получить все скидки на список товаров

        discounts: список иснтансов скидок
        """
        discounts = []
        print('Calculated twice')
        products = self.cart.get_goods()
        print(products)
        for product in products:
            discounts += self.get_all_discounts_for_product(product)

        print(f'Cart all discounts: {discounts}')
        return set(discounts)

    def get_priority_discounts_for_products(self):
        """
        получить приоритетные скидки на список товаров

        discounts: список иснтансов скидок
        """
        priority_discounts = []
        print('Calculated once')
        discounts = self.get_all_discounts_for_products()
        for discount in discounts:
            class_name = discount.__class__.__name__
            if class_name == 'CartDiscount':
                if self.check_cart_discount(discount):
                    priority_discounts.append(discount)
            elif class_name == 'ProductDiscount':
                if discount.set_discount:
                    if self.check_set_discount(discount):
                        print(self.check_set_discount(discount))
                        priority_discounts.append(discount)
                else:
                    priority_discounts.append(discount)
            else:
                priority_discounts.append(discount)

        print(f'Cart priority discounts: {priority_discounts}')
        return priority_discounts

    @staticmethod
    def get_all_discounts_for_product(product):
        """
        получить все скидки на товар

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
        получить приоритетные скидки на товар

        discounts: список иснтансов скидок
        """
        product_discounts = set(self.get_all_discounts_for_product(product))
        print(f'Product_discounts: {product_discounts}')
        result_discounts = set(self.discounts) & product_discounts
        priority = 0
        for discount in result_discounts:
            discount_priority = int(discount.priority)
            print(discount_priority)
            if discount_priority > int(priority):
                priority = discount.priority
                print(priority)
        result_discounts = [discount for discount in result_discounts if int(discount.priority) == int(priority)]
        return result_discounts

    def check_cart_discount(self, discount) -> bool:
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
        if discount.total_sum_min_threshold < self.cart.get_total_sum() < discount.total_sum_max_threshold:
            return True
        return False

    def check_set_discount(self, discount):
        cart_products = self.cart.get_goods()
        if cart_products.__class__.__name__ == 'QuerySet':
            cart_products = [item.seller_product for item in cart_products]
        else:
            cart_products = [item['seller_product'] for item in cart_products]
        discount_set_products = [item for item in discount.seller_products.all()]
        if set(discount_set_products) & set(cart_products) == set(discount_set_products):
            return True
        return False

    def get_discounted_price(self, product, class_name: str = 'CartDiscount', price: float = None) -> Decimal :
        """
        расчитать цену со скидкой
        """
        prices = []
        product_discounts = self.get_priority_discounts_for_product(product)
        print(f'Product discounts: {product_discounts}')

        if product.__class__.__name__ == 'OrderProduct':
            price = product.seller_product.price
        else:
            price = product['seller_product'].price

        if product_discounts:
            for discount in product_discounts:
                if discount.__class__.__name__ == 'ProductDiscount':
                    if discount.set_discount is True and discount.amount > 0:
                        set_sum = sum([item.price for item in discount.seller_products.all()])
                        set_sum_with_discount = set_sum - Decimal(discount.amount)
                        price = Decimal(price * set_sum_with_discount / set_sum)

                elif discount.amount:
                    price -= Decimal(discount.amount)
                else:
                    price *= Decimal((100 - discount.percent) / 100)

                prices.append(price)
        if prices:
            price = max(prices)

        if price < 1:
            price = 1

        return Decimal(round(price, 2))
