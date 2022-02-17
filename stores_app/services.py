from django.db.models import QuerySet

from discounts_app.models import Discount
from stores_app.models import Seller, SellerProduct
from goods_app.models import Product, ProductCategory


class QueryMixin:

    @classmethod
    def create_store(cls, user, form) -> None:
        """
        Create new Seller instance
        """
        Seller.objects.create(owner=user, **form.cleaned_data)

    @classmethod
    def get_store(cls, slug: str) -> QuerySet:
        """
        Get store with slug
        """
        return Seller.objects.select_related('owner').get(slug=slug)

    @classmethod
    def edit_store(cls, store_slug: str, form) -> None:
        """
        Update Seller instance
        """
        Seller.objects.filter(slug=store_slug).update(**form.cleaned_data)

    @classmethod
    def get_user_stores(cls, user) -> QuerySet:
        """
        Get all stores by user
        """
        return Seller.objects.filter(owner=user)

    @classmethod
    def remove_store(self, store_id: int) -> None:
        """
        Remove store
        """
        Seller.objects.filter(id=store_id).delete()

    @classmethod
    def create_seller_product(cls, form) -> None:
        """
        Create new product in store by seller
        """
        print(form.cleaned_data)
        SellerProduct.objects.create(**form.cleaned_data)

    @classmethod
    def get_seller_products(cls, user) -> QuerySet:
        """
        Get all products, added by user
        """
        return SellerProduct.objects.select_related('seller', 'discount', 'product')\
                                    .filter(seller__owner=user)

    @classmethod
    def remove_seller_product(self, product_id: int) -> None:
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




