from typing import Dict, Iterable

from django import template
from django.core.cache import cache

from goods_app.models import ProductCategory


register = template.Library()


@register.simple_tag()
def get_tree_dict() -> Dict:
    categories_cache_key = 'categories:{}'.format('all')
    categories = cache.get(categories_cache_key)
    if not categories:
        categories = ProductCategory.objects.select_related('parent').all()
        cache.set(categories_cache_key, categories, 60 * 60)
    res_dict = dict()
    for elem in categories:
        if elem.parent_id:
            res_dict.setdefault(elem.parent, [])
            res_dict[elem.parent].append(elem)
        else:
            res_dict.setdefault(elem, [])
    return res_dict


@register.filter(name='times')
def times(number: int) -> Iterable:
    return range(number)
