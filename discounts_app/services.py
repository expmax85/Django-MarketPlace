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
        for product in products:
            discounts += self.get_all_discounts_for_product(product)

        return discounts

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
            if class_name == 'ProductDiscount':
                priority_discounts.append(discount)

        return priority_discounts

    def get_all_discounts_for_product(self, product):
        """
        получить все скидки на товар

        discounts: список иснтансов скидок
        """
        discounts = []

        if product.__class__.__name__ == 'OrderProduct':
            cart_discounts = product.seller_product.seller.cart_discounts.filter(is_active=True).all()
            category_discounts = product.seller_product.product.category.group_discounts.filter(is_active=True).all()
            product_discounts = product.seller_product.product_discounts.filter(is_active=True).all()
        else:
            cart_discounts = product['seller_product'].seller.cart_discounts.filter(is_active=True).all()
            category_discounts = product['seller_product'].product.category.group_discounts.filter(is_active=True).all()
            product_discounts = product['seller_product'].product_discounts.filter(is_active=True).all()
        if cart_discounts:
            discounts += cart_discounts
        if category_discounts:
            discounts += category_discounts
        if product_discounts:
            discounts += product_discounts

        print(discounts)
        return discounts

    def get_priority_discounts_for_product(self, product):
        """
        получить приоритетные скидки на товар

        discounts: список иснтансов скидок
        """
        cart_discounts_all = set(self.discounts)
        product_discounts = set(self.get_all_discounts_for_product(product))
        result_discounts = cart_discounts_all & product_discounts

        return result_discounts

    def get_discounted_price(self, product, class_name: str = 'CartDiscount', price: float = None) -> Decimal:
        """
        расчитать цену со скидкой
        """
        prices = []
        product_discounts = self.get_priority_discounts_for_product(product)
        print(f'All discounts for cart - {product_discounts}')
        if product.__class__.__name__ == 'OrderProduct':
            price = product.seller_product.price
        else:
            price = product['seller_product'].price
        if product_discounts:
            for discount in product_discounts:
                if discount.amount:
                    price -= Decimal(discount.amount)
                else:
                    price *= Decimal((100 - discount.percent) / 100)

                prices.append(price)
        if prices:
            price = max(prices)
        # if product in self.cart.get_goods():
        #     if len(self.cart) > 2:
        #         price = 300
        #     else:
        #         price = 400
        # else:
        #     price = 600
        return Decimal(round(price, 2))
