from typing import Dict

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet
from django.http import HttpRequest

from goods_app.models import ProductComment, Product
from stores_app.models import SellerProduct
from settings_app.config_project import OPTIONS


class CurrentProduct:

    def __init__(self, **kwargs) -> None:
        if 'slug' in kwargs:
            self.product = Product.objects.get(slug=kwargs['slug'])
        elif 'instance' in kwargs:
            self.product = kwargs['instance']
        else:
            raise ValueError

    @property
    def get_product(self) -> Product:
        return self.product

    @property
    def get_sellers(self) -> QuerySet:
        sellers_cache_key = 'sellers:{}'.format(self.product.id)
        sellers = cache.get(sellers_cache_key)
        if not sellers:
            sellers = SellerProduct.objects.select_related('seller', 'product', 'product__category') \
                                   .filter(product=self.product) \
                                   .order_by('price')
            cache.set(sellers_cache_key, sellers, 24 * 60 * 60)
        return sellers

    @property
    def get_best_offer(self) -> QuerySet:
        return self.get_sellers.first()

    @property
    def get_specifications(self) -> QuerySet:
        specifications_cache_key = 'specifications:{}'.format(self.product.id)
        specifications = cache.get(specifications_cache_key)
        if not specifications:
            specifications = self.product.specifications.all()
            cache.set(specifications_cache_key, specifications, 24 * 60 * 60)
        return specifications

    @property
    def get_tags(self) -> QuerySet:
        tags_cache_key = 'tags:{}'.format(self.product.id)
        tags = cache.get(tags_cache_key)
        if not tags:
            tags = self.product.tags.all()
            cache.set(tags_cache_key, tags, 24 * 60 * 60)
        return tags

    @property
    def get_reviews(self) -> QuerySet:
        reviews_cache_key = 'reviews:{}'.format(self.product.id)
        reviews = cache.get(reviews_cache_key)
        if not reviews:
            reviews = self.product.product_comments.all()
            cache.set(reviews_cache_key, reviews, 24 * 60 * 60)
        return reviews

    def get_review_page(self, queryset: QuerySet, page: int) -> Dict:
        reviews_count = queryset.count()
        reviews = queryset.values('author', 'content', 'added')
        paginator = Paginator(reviews, per_page=OPTIONS['general__review_size_page'])
        page_obj = paginator.get_page(page)
        json_dict = {
            'comments': list(page_obj.object_list),
            'has_previous': None if page_obj.has_previous() is False
            else "previous",
            'previous_page_number': page_obj.number - 1,
            'num_pages': page_obj.paginator.num_pages,
            'number': page_obj.number,
            'has_next': None if page_obj.has_next() is False
            else "next",
            'next_page_number': page_obj.number + 1,
            'empty_pages': None if page_obj.paginator.num_pages < 2
            else "not_empty",
            'reviews_count': reviews_count
        }
        return json_dict

    def calculate_product_rating(self) -> None:
        rating = ProductComment.objects.only('rating') \
            .filter(product_id=self.product.id) \
            .aggregate(Avg('rating'))['rating__avg']
        if rating:
            self.product.rating = round(float(rating), 0)
            self.product.save(update_fields=['rating'])

    def get_context_data(self, *args) -> Dict:
        context = dict()
        for arg in args:
            try:
                context[str(arg)] = getattr(self, ''.join(['get_', str(arg)]))
            except AttributeError as err:
                raise AttributeError(err)
        return context


@receiver(post_save, sender=ProductComment)
def comment_post_save_handler(sender, **kwargs) -> None:
    if kwargs['created']:
        product_id = kwargs['instance'].product_id
        cache.delete('reviews:{}'.format(product_id))


def context_pagination(request: HttpRequest, queryset: QuerySet, size_page: int = 3) -> Paginator:
    """
    Функция для создания пагинации
    :return: Paginator
    """
    paginator = Paginator(queryset, size_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
