from typing import List
# from stores_app.models import SellerProduct
# from discounts_app.models import Discount
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

    # @classmethod
    # def get_all_discounts_for_products(cls, products) -> List[Discount]:
    #     """
    #     получить все скидки на список товаров
    #
    #     discounts: список иснтансов скидок
    #     """
    #     discounts = Discount.objects.all()
    #     return discounts
    #
    # @classmethod
    # def get_all_discounts_for_product(cls, product) -> List[Discount]:
    #     """
    #     получить все скидки на товар
    #
    #     discounts: список иснтансов скидок
    #     """
    #     discounts = Discount.objects.all()
    #     return discounts
    #
    # @classmethod
    # def get_priority_discounts_for_products(cls, product) -> List[Discount]:
    #     """
    #     получить приоритетные скидки на список товаров
    #
    #     discounts: список иснтансов скидок
    #     """
    #     priority_discounts = Discount.objects.all()
    #     return priority_discounts
    #
    # @classmethod
    # def get_priority_discounts_for_product(cls, product) -> List[Discount]:
    #     """
    #     получить приоритетные скидки на товар
    #
    #     discounts: список иснтансов скидок
    #     """
    #     priority_discounts = Discount.objects.all()
    #     return priority_discounts

    @classmethod
    def get_discounted_price(cls, product, price: float = None) -> Decimal:
        """
        расчитать цену со скидкой
        """
        try:
            discount = product.product_discounts.filter(priority=1)[0].percent
        except IndexError:
            discount = 0
        if not price:
            price = product.price

        price = float(price) * (100 - discount) / 100
        return Decimal(price)
