from typing import Callable

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.registries import global_preferences_registry


def get_help_text(**kwargs) -> Callable:
    """
    Get help text for image fields about needed size
    """
    help_text = 'error'
    if kwargs.get('size'):
        OPTIONS = global_preferences_registry.manager().by_name()
        max_size = OPTIONS['max_size_file']
        help_text = _(f'Load image with max file size {max_size}MB')
    elif kwargs.get('resolution'):
        min_width, min_height = settings.MIN_RESOLUTION
        max_width, max_height = settings.MAX_RESOLUTION
        help_text = _(f'Load image with sizes from {min_width}x{min_height} to {max_width}x{max_height}')
    return mark_safe(f'<span style="color:#417690; font-size:12px;">{help_text}</span>')


def check_image_size(image) -> bool:
    """
    Validate image size
    """
    OPTIONS = global_preferences_registry.manager().by_name()
    max_size = OPTIONS['max_size_file']
    try:
        if image.size > max_size * 1024 ** 2:
            raise ValidationError(_(f'File must be size less than {max_size}MB'))
        return True
    except (ValueError, AttributeError):
        return False


def check_image_resolution(image) -> bool:
    """
    Validate image resolution
    """
    min_width, min_height = settings.MIN_RESOLUTION
    max_width, max_height = settings.MAX_RESOLUTION
    try:
        from PIL import Image
        img = Image.open(image)
        if img.height < min_height or img.width < min_width:
            raise ValidationError(_('resolution image is too small.'))
        if img.height > max_height or img.width > max_width:
            raise ValidationError(_('resolution image is too big.'))
        img.close()
        return True
    except (ValueError, AttributeError):
        return False
