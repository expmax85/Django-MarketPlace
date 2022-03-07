from typing import Dict, Iterable

from django import template
from goods_app.models import ProductCategory


register = template.Library()


@register.simple_tag()
def get_tree_dict() -> Dict:
    categories = ProductCategory.objects.select_related('parent').all()
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
