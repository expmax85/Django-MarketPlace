from typing import Dict

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet
from goods_app.models import Product, ProductComment


def calculate_product_rating(product: 'Product') -> None:
    rating = ProductComment.objects.only('rating').filter(product_id=product.id).aggregate(Avg('rating'))['rating__avg']
    if rating:
        product.rating = round(float(rating), 0)
        product.save(update_fields=['rating'])


def get_reviews(product: 'Product'):
    reviews_cache_key = 'reviews:{}'.format(product.id)
    reviews = cache.get(reviews_cache_key)
    if not reviews:
        reviews = product.product_comments.all()
        cache.set(reviews_cache_key, reviews, 120 * 60)
    return reviews


def context_pagination(request, queryset: QuerySet, size_page: int = 3) -> Paginator:
    """
    Функция для создания пагинации
    :return: Paginator
    """
    paginator = Paginator(queryset, size_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

