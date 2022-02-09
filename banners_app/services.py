from datetime import datetime
from banners_app.models import Banner


def banner():
    banners = Banner.objects.prefetch_related('discount'). \
        filter(discount__valid_from__lte=datetime.now()). \
        filter(discount__valid_to__gte=datetime.now()). \
        order_by('?')[:3]

    return banners
