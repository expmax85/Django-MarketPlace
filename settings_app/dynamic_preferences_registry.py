import datetime
from decimal import Decimal

from django.utils.translation import gettext_lazy as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import DecimalPreference, IntegerPreference, TimePreference, ChoicePreference
from dynamic_preferences.registries import global_preferences_registry


general = Section('general')


@global_preferences_registry.register
class ShippingRegularPrice(DecimalPreference):
    section = general
    name = 'regular_shipping'
    help_text = _('Set the regular shipping amount')
    default = Decimal('10.00')
    required = True
    verbose_name = _('Regular shipping price')


@global_preferences_registry.register
class ShippingExpressPrice(DecimalPreference):
    section = general
    name = 'express_shipping'
    help_text = _('Set the express shipping amount')
    default = Decimal('20.00')
    required = True
    verbose_name = _('Express shipping price')


@global_preferences_registry.register
class ReviewsSizePage(IntegerPreference):
    section = general
    name = 'review_size_page'
    help_text = _('Set the count reviews, showing on product detail page')
    default = 3
    required = True
    verbose_name = _('Reviews size page')


@global_preferences_registry.register
class DaysDuration(IntegerPreference):
    section = general
    name = 'days_duration'
    help_text = _('Set the days duration for updating limited deal product')
    default = 1
    required = True
    verbose_name = _('Days duration limited deal')


@global_preferences_registry.register
class TimeUpdate(TimePreference):
    section = general
    name = 'time_update'
    help_text = _('Set the time update for limited deal product')
    default = datetime.time(hour=00, minute=00, second=00)
    required = True
    verbose_name = _('Time update limited deal')


@global_preferences_registry.register
class CountLimitedProducts(IntegerPreference):
    section = general
    name = 'count_limited_products'
    help_text = _('Set the count limited products, showing on main page')
    default = 8
    required = True
    verbose_name = _('Count limited products')


@global_preferences_registry.register
class SortIndexProducts(ChoicePreference):
    section = general
    name = 'sort_index'
    help_text = _('Set the count hot offers, showing on main page')
    choices = (
        ('-date added', _('date_added')),
        ('-viewed', _('viewed_count')),
    )
    default = '-date_added'
    required = True
    verbose_name = _('Sort index products')


@global_preferences_registry.register
class CountPopularProducts(IntegerPreference):
    section = general
    name = 'count_popular_products'
    help_text = _('Set the count popular products, showing on main page')
    default = 8
    required = True
    verbose_name = _('Count popular products')


@global_preferences_registry.register
class CountHotProducts(IntegerPreference):
    section = general
    name = 'count_hot_offers'
    help_text = _('Set the count hot offers, showing on main page')
    default = 8
    required = True
    verbose_name = _('Count hot offers')


@global_preferences_registry.register
class TimeExpireBanners(IntegerPreference):
    section = general
    name = 'banners_time_expire'
    help_text = _('Set the time update banners (in minutes)')
    default = 5
    required = True
    verbose_name = _('Banners time expire')
