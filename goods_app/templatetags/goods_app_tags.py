from typing import Dict, Iterable

from django import template
from goods_app.services.catalog import get_categories


register = template.Library()


@register.simple_tag()
def get_tree_dict() -> Dict:
    categories = get_categories()
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


@register.inclusion_tag('elems/card.html')
def cards(products, **kwargs):
    slider = False
    exclude = -1
    if kwargs.get('slider'):
        slider = True
    if kwargs.get('exclude'):
        exclude = kwargs['exclude']
    return {'products': products,
            'slider': slider,
            'exclude': exclude}
