import datetime
import random
from typing import Dict, Iterable

from django import template
from goods_app.models import ProductCategory
from stores_app.models import SellerProduct

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


# @register.inclusion_tag('limited-deal.html')
# def limited_deal(deals, days=1, hours=None, update_time='12:00'):
#     item.update_product()
#     return {'product': product,
#             'end_time': end_time.strftime("%d.%m.%Y %H:%M")}
