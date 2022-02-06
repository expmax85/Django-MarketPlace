from datetime import datetime
from banners_app.models import Banner
from django.core.cache import cache


def banner(request):
    try:
        user_mark = request.user.email
    except AttributeError:
        user_mark = 'some@some.com'

    banners_cache_key = f'banners:{user_mark}'
    banners = Banner.objects.prefetch_related('discount'). \
        filter(discount__valid_from__lte=datetime.now()). \
        filter(discount__valid_to__gte=datetime.now()). \
        order_by('?')[:3]

    cache.get_or_set(banners_cache_key, banners, 600)

    return banners
