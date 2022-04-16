from typing import Dict, List

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet
from django.http import HttpRequest
from dynamic_preferences.registries import global_preferences_registry

from discounts_app.services import get_discounted_prices_for_seller_products
from goods_app.models import ProductComment, Product
from stores_app.models import SellerProduct


class CurrentProduct:
    """
    A class for working with a Product instance. You can get a product by its slug or directly instance

    Allowed methods and properties:
    get_product,
    get_sellers,
    get_calculate_prices(),
    get_specifications,
    get_tags,
    get_reviews,
    get_review_page(queryset, page),
    calculate_product_rating()
    """

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
    def get_sellers(self) -> List:
        """
        Method to get all sellers, who have this product. Returns ordering queryset by price
        """
        sellers_cache_key = 'sellers:{}'.format(self.product.id)
        queryset = cache.get(sellers_cache_key)
        if not queryset:
            queryset = SellerProduct.objects.select_related('seller', 'product',
                                                            'product__category',
                                                            'product__category__parent') \
                                            .filter(product=self.product)
            cache.set(sellers_cache_key, queryset, 24 * 60 * 60)
        sellers = get_discounted_prices_for_seller_products(queryset)
        sellers = sorted(list(sellers), key=lambda x: x[1] if x[1] else x[0].price)
        return sellers

    def get_calculate_prices(self) -> Dict:
        """
        Method for getting best seller and average prices
        """
        all_sellers = sorted(self.get_sellers, key=lambda x: x[0].quantity, reverse=True)
        if all_sellers:
            list_price = [x[0].price for x in all_sellers]
            avg_price = round((sum(list_price) / len(list_price)), 2)
            list_price_after_discount = [x[1] if x[1] else x[0].price for x in all_sellers]
            avg_price_after_discount = round((sum(list_price_after_discount) / len(list_price_after_discount)), 2)
        else:
            return {
                'best_offer': False,
                'avg_price': "",
                'avg_price_after_discount': "not determine"
            }

        try:
            temp = [item[0].quantity for item in all_sellers]
            index = temp.index(0)
            all_sellers = all_sellers[:index]
        except ValueError:
            pass

        try:
            best_seller = min(all_sellers, key=lambda x: x[1] if x[1] else x[0].price)
        except ValueError:
            return {
                'best_offer': False,
                'avg_price': avg_price,
                'avg_price_after_discount': avg_price_after_discount
            }
        return {
            'best_offer': best_seller[0],
            'avg_price': avg_price,
            'avg_price_after_discount': avg_price_after_discount,
        }

    @property
    def get_specifications(self) -> QuerySet:
        """
        Method for getting all specifications product
        """
        specifications_cache_key = 'specifications:{}'.format(self.product.id)
        specifications = cache.get(specifications_cache_key)
        if not specifications:
            specifications = self.product.specifications.all()
            cache.set(specifications_cache_key, specifications, 24 * 60 * 60)
        return specifications

    @property
    def get_tags(self) -> QuerySet:
        """
        Method for getting all tags product
        """
        tags_cache_key = 'tags:{}'.format(self.product.id)
        tags = cache.get(tags_cache_key)
        if not tags:
            tags = self.product.tags.all()
            cache.set(tags_cache_key, tags, 24 * 60 * 60)
        return tags

    @property
    def get_reviews(self) -> QuerySet:
        """
        Method for getting all reviews product
        """
        reviews_cache_key = 'reviews:{}'.format(self.product.id)
        reviews = cache.get(reviews_cache_key)
        if not reviews:
            reviews = self.product.product_comments.all()
            cache.set(reviews_cache_key, reviews, 24 * 60 * 60)
        return reviews

    @classmethod
    def get_review_page(cls, queryset: QuerySet, page: int) -> Dict:
        """
        Method for getting reviews page to pass to javascript. Returns dict with queryset page reviews
        and data for pagination
        """
        reviews_count = queryset.count()
        reviews = queryset.values('author', 'user__avatar', 'content', 'added')
        OPTIONS = global_preferences_registry.manager().by_name()
        paginator = Paginator(reviews, per_page=OPTIONS['review_size_page'])
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
            'reviews_count': reviews_count,
            'media': settings.MEDIA_URL
        }
        return json_dict

    def update_product_rating(self) -> None:
        """
        Method for calculating and updating product rating, when the review added
        """
        rating = ProductComment.objects.only('rating') \
            .filter(product_id=self.product.id) \
            .aggregate(Avg('rating'))['rating__avg']
        if rating:
            self.product.rating = round(float(rating), 0)
            self.product.save(update_fields=['rating'])


def context_pagination(request: HttpRequest, queryset: QuerySet, size_page: int = 3) -> Paginator:
    """
    Function for creating pagination
    """
    paginator = Paginator(queryset, size_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
