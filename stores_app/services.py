import os

from django.contrib import messages
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_delete

from config.settings import MEDIA_ROOT
from discounts_app.models import Discount
from stores_app.models import Seller, SellerProduct
from goods_app.models import Product, ProductCategory


# Set custom level messages for django.contrib.messages
SUCCESS_DEL_PRODUCT = 100
SUCCESS_DEL_STORE = 110


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

    @classmethod
    def remove_store(cls, request) -> None:
        """
        Remove store
        """
        store = Seller.objects.get(id=request.GET.get('id'))
        messages.add_message(request, SUCCESS_DEL_STORE,
                             _(f'The {store.name} was removed'))
        store.delete()

    @classmethod
    def get_seller_products(cls, user) -> QuerySet:
        """
        Get all products, added by user
        """
        return SellerProduct.objects.select_related('seller', 'discount', 'product')\
                                    .filter(seller__owner=user)

    @classmethod
    def remove_seller_product(cls, request) -> None:
        """
        Remove store
        """
        item = SellerProduct.objects.select_related('seller', 'product').get(id=request.GET.get('id'))
        messages.add_message(request, SUCCESS_DEL_PRODUCT,
                             _(f'Product {item.product.name} from the store {item.seller.name} was removed'))
        item.delete()

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
        """
        Method for remove old file, when update the store-logo for example
        """
        path = os.path.normpath(os.path.join(MEDIA_ROOT, str(file)))
        if os.path.exists(path):
            os.remove(path)


def delete_IconFile(**kwargs):
    """
    The signal for removing icon Seller, when the store is deleting
    """
    file = kwargs.get('instance')
    file.icon.delete(save=False)


post_delete.connect(delete_IconFile, Seller)
