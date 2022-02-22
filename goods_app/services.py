from django.db.models import QuerySet
from django.http import HttpRequest
from goods_app.models import ProductCategory


# TODO сервис добавления комментариев к товару


def create_comment(request: HttpRequest) -> None:
    pass


def get_all_product_categories() -> QuerySet:
    all_categories = ProductCategory.objects.all()

    return all_categories
