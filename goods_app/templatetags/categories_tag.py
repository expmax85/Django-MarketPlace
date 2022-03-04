from django import template
from goods_app.models import ProductCategory

register = template.Library()


@register.simple_tag()
def get_tree_dict():
    categories = ProductCategory.objects.all()

    res_dict = {elem: [] for elem in categories}
    ch = []

    for elem in categories:

        if elem.get_children():
            res_dict[elem].extend([x for x in elem.get_children()])
            ch.extend(elem.get_children())
    for e in ch:
        del res_dict[e]

    return res_dict
