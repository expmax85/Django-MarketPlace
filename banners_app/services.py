from datetime import datetime
from banners_app.models import Banner


def banner():
    """Функция получения трех случаных баннеров для главной страницы"""
    banners = Banner.objects.prefetch_related('discount'). \
        filter(discount__valid_from__lte=datetime.now()). \
        filter(discount__valid_to__gte=datetime.now()). \
        filter(discount__is_active=True). \
        order_by('?')[:3]
    return banners
