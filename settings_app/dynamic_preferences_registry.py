import datetime
from decimal import Decimal

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import DecimalPreference, IntegerPreference, TimePreference, ChoicePreference
from dynamic_preferences.registries import global_preferences_registry


general = Section('general')


@global_preferences_registry.register
class ShippingRegularPrice(DecimalPreference):
    section = general
    name = 'regular_shipping'
    default = Decimal('10.00')
    required = True
    verbose_name = 'Regular shipping price'


@global_preferences_registry.register
class ShippingExpressPrice(DecimalPreference):
    section = general
    name = 'express_shipping'
    default = Decimal('20.00')
    required = True
    verbose_name = 'Express shipping price'


@global_preferences_registry.register
class ReviewsSizePage(IntegerPreference):
    section = general
    name = 'review_size_page'
    default = 3
    required = True
    verbose_name = 'Reviews size page'


@global_preferences_registry.register
class DaysDuration(IntegerPreference):
    section = general
    name = 'days_duration'
    default = 1
    required = True
    verbose_name = 'Days duration limited deal'


@global_preferences_registry.register
class TimeUpdate(TimePreference):
    section = general
    name = 'time_update'
    default = datetime.time(hour=00, minute=00, second=00)
    required = True
    verbose_name = 'Time update limited deal'


@global_preferences_registry.register
class CountLimitedProducts(IntegerPreference):
    section = general
    name = 'count_limited_products'
    default = 3
    required = True
    verbose_name = 'Count limited products'


@global_preferences_registry.register
class SortIndexProducts(ChoicePreference):
    section = general
    name = 'sort_index'
    choices = (
        ('date added', 'date_added'),
        ('viewed', 'viewed_count'),

    )
    default = 'date_added'
    required = True
    verbose_name = 'Sort index products'


@global_preferences_registry.register
class CountLimitedProducts(IntegerPreference):
    section = general
    name = 'count_popular_products'
    default = 8
    required = True
    verbose_name = 'Count popular products'
