from django import template
from django.db import reset_queries, connection

from goods_app.models import ProductCategory

register = template.Library()


@register.simple_tag()
def get_tree_dict():
    categories = ProductCategory.objects.select_related('parent').all()
    res_dict = dict()
    for elem in categories:
        if elem.parent_id:
            res_dict.setdefault(elem.parent, [])
            res_dict[elem.parent].append(elem)
        else:
            res_dict.setdefault(elem, [])
    #
    # res_dict = {elem: [] for elem in categories}
    # ch = []
    #
    # for elem in categories:
    #
    #     if elem.get_children():
    #         res_dict[elem].extend([x for x in elem.get_children()])
    #         ch.extend(elem.get_children())
    # for e in ch:
    #     del res_dict[e]
    # print(res_dict)
    return res_dict
