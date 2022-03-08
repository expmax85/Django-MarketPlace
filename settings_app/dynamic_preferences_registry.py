from decimal import Decimal

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import DecimalPreference
from dynamic_preferences.registries import global_preferences_registry


shipping = Section('general')


@global_preferences_registry.register
class ShippingPrice(DecimalPreference):
    section = shipping
    name = 'shipping_price'
    default = Decimal('10.00')
    required = True
    verbose_name = 'Shipping price'
