import os

from django.db.models import QuerySet

from config.settings import MEDIA_ROOT
from discounts_app.models import Discount
from stores_app.models import Seller, SellerProduct
from goods_app.models import Product, ProductCategory


class QueryMixin:

    @classmethod
    def get_store(cls, slug: str) -> QuerySet:
        """
        Get store with slug
        """
        return Seller.objects.select_related('owner').get(slug=slug)

    @classmethod
    def get_user_stores(cls, user) -> QuerySet:
        """
        Get all stores by user
        """
        return Seller.objects.filter(owner=user)

    def remove_store(self, store_id: int) -> None:
        """
        Remove store
        """
        store = Seller.objects.get(id=store_id)
        self.remove_old_file(str(store.icon))
        store.delete()

    @classmethod
    def get_seller_products(cls, user) -> QuerySet:
        """
        Get all products, added by user
        """
        return SellerProduct.objects.select_related('seller', 'discount', 'product')\
                                    .filter(seller__owner=user)

    @classmethod
    def remove_seller_product(cls, product_id: int) -> None:
        """
        Remove store
        """
        SellerProduct.objects.filter(id=product_id).delete()

    @classmethod
    def get_categories(cls) -> QuerySet:
        """
        Get all categories
        """
        return ProductCategory.objects.all()

    @classmethod
    def get_products(cls, **kwargs) -> QuerySet:
        if 'category_id' in kwargs.keys():
            return Product.objects.select_related('category').filter(category=kwargs.get('category_id'))
        else:
            return Product.objects.select_related('category').all()

    @classmethod
    def get_discounts(cls) -> QuerySet:
        return Discount.objects.all()

    @classmethod
    def remove_old_file(cls, file: str) -> None:
        path = os.path.normpath(os.path.join(MEDIA_ROOT, str(file)))
        if os.path.exists(path):
            os.remove(path)
