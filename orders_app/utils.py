import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """ Отбрасывает Decimal у объекта из queryset """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)