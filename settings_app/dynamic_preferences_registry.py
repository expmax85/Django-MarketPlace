import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import DecimalPreference, IntegerPreference, TimePreference
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

    def validate(self, value):
        if value < 0:
            raise ValidationError(_('Wrong price value! Must be positive'))


@global_preferences_registry.register
class ShippingExpressPrice(DecimalPreference):
    section = general
    name = 'express_shipping'
    help_text = _('Set the express shipping amount')
    default = Decimal('20.00')
    required = True
    verbose_name = _('Express shipping price')

    def validate(self, value):
        if value < 0:
            raise ValidationError(_('Wrong price value! Must be positive'))


@global_preferences_registry.register
class ReviewsSizePage(IntegerPreference):
    section = general
    name = 'review_size_page'
    help_text = _('Set the count reviews, showing on product detail page')
    default = 3
    required = True
    verbose_name = _('Reviews size page')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong size value! Must be more than 0'))


@global_preferences_registry.register
class DaysDuration(IntegerPreference):
    section = general
    name = 'days_duration'
    help_text = _('Set the days duration for updating limited deal product')
    default = 1
    required = True
    verbose_name = _('Days duration limited deal')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong days value! Must be more than 0'))


@global_preferences_registry.register
class TimeUpdate(TimePreference):
    section = general
    name = 'time_update'
    help_text = _('Set the time update for limited deal product')
    default = datetime.time(hour=00, minute=00, second=00)
    required = True
    verbose_name = _('Time update limited deal')

    def validate(self, value):
        if value <= datetime.datetime.now():
            raise ValidationError(_('Wrong date value! Must be more than 0'))


@global_preferences_registry.register
class CountLimitedProducts(IntegerPreference):
    section = general
    name = 'count_limited_products'
    help_text = _('Set the count limited products, showing on main page')
    default = 8
    required = True
    verbose_name = _('Count limited products')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong count value! Must be more than 0'))


@global_preferences_registry.register
class CountPopularProducts(IntegerPreference):
    section = general
    name = 'count_popular_products'
    help_text = _('Set the count popular products, showing on main page')
    default = 8
    required = True
    verbose_name = _('Count popular products')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong count value! Must be more than 1'))


@global_preferences_registry.register
class CountHotProducts(IntegerPreference):
    section = general
    name = 'count_hot_offers'
    help_text = _('Set the count hot offers, showing on main page')
    default = 8
    required = True
    verbose_name = _('Count hot offers')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong count value! Must be more than 1'))


@global_preferences_registry.register
class TimeExpireBanners(IntegerPreference):
    section = general
    name = 'banners_time_expire'
    help_text = _('Set the time update banners (in minutes)')
    default = 5
    required = True
    verbose_name = _('Banners time expire')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong banners expire value! Must be more than 1 (minutes)'))


@global_preferences_registry.register
class MaxFileSize(IntegerPreference):
    section = general
    name = 'max_size_file'
    help_text = _('Set the max image file sizes in MB')
    default = 2
    required = True
    verbose_name = _('Max image files size')

    def validate(self, value):
        if value < 1:
            raise ValidationError(_('Wrong size file value! Must be more than 1 (MB)'))
