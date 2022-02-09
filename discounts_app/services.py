from typing import List
from stores_app.models import SellerProduct
from discounts_app.models import Discount


class DiscountsService:
    """
    Сервис расчета скидок

    get_all_discounts_for_products: метод получения всех скидок на список товаров
    get_all_discounts_for_product: метод получения всех скидок на список товаров
    get_priority_discounts_for_products: метод получения приоритетных скидок на список товаров
    get_priority_discounts_for_product: метод получения приоритетных скидок на список товаров
    get_discounted_price: получение цены товарова с учетом скидки
    """

    @classmethod
    def get_all_discounts_for_products(cls, products: [SellerProduct]) -> List[Discount]:
        """
        получить все скидки на список товаров

        discounts: список иснтансов скидок
        """
        discounts = Discount.objects.all()
        return discounts

    @classmethod
    def get_all_discounts_for_product(cls, product: SellerProduct) -> List[Discount]:
        """
        получить все скидки на товар

        discounts: список иснтансов скидок
        """
        discounts = Discount.objects.all()
        return discounts

    @classmethod
    def get_priority_discounts_for_products(cls, product: [SellerProduct]) -> List[Discount]:
        """
        получить приоритетные скидки на список товаров

        discounts: список иснтансов скидок
        """
        priority_discounts = Discount.objects.all()
        return priority_discounts

    @classmethod
    def get_priority_discounts_for_product(cls, product: SellerProduct) -> List[Discount]:
        """
        получить приоритетные скидки на товар

        discounts: список иснтансов скидок
        """
        priority_discounts = Discount.objects.all()
        return priority_discounts

    @classmethod
    def get_discounted_price(cls, product: SellerProduct, price: float = None) -> float:
        """
        расчитать цену со скидкой
        """
        discount = 1
        if not price:
            price = product.price

        price = price * discount
        return price
