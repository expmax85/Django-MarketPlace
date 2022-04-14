import json
from decimal import Decimal

from stores_app.models import SellerProduct


def check_stock(product: SellerProduct, delta: int) -> bool:
    """ Проверка наличия на складе """
    if product.quantity >= delta:
        product.quantity -= delta
        product.save()
        return True
    return False


class DecimalEncoder(json.JSONEncoder):
    """ Отбрасывает Decimal у объекта из queryset """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
