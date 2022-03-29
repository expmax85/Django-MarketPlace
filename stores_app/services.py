import os
from typing import Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_delete
from django.core.cache import cache

from config.settings import MEDIA_ROOT, SUCCESS_DEL_STORE, SUCCESS_DEL_PRODUCT
from orders_app.models import Order, ViewedProduct
from stores_app.models import Seller, SellerProduct
from goods_app.models import Product


User = get_user_model()


class StoreServiceMixin:
    """
    Mixin with functions for queries by models Seller and SellerProduct

    All available methods:
    get_store(slug) - get Seller instance with slug=slug
    get_user_stores(user) - get all Seller models by owner=user
    create_seller_product(data) - create SelleProduct instance
    edit_seller_product(data, instance) - edit SellerProduct instance
    get_products(query params) - get products
    get_seller_products(user) - get SellerProducts query by Sellers owner=user
    get_viewed_products(user) - get all viewed SellerProduct instances
    remove_seller_product(request) - Remove SellerProduct instance with id=request.id
    remove_store(request) - remove Seller instance with id=request.id=request
    """

    @classmethod
    def get_store(cls, slug: str) -> QuerySet:
        """
        Get store with slug
        """
        return Seller.objects.select_related('owner').get(slug=slug)

    @classmethod
    def get_user_stores(cls, user: User) -> QuerySet:
        """
        Get all stores by user
        """
        stores_cache_key = 'stores:{}'.format(user.id)
        stores = cache.get(stores_cache_key)
        if not stores:
            stores = Seller.objects.filter(owner=user)
            cache.set(stores_cache_key, stores, 60 * 60)
        return stores

    @classmethod
    def remove_store(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        store = Seller.objects.only('name').get(id=request.GET.get('id'))
        messages.add_message(request, SUCCESS_DEL_STORE,
                             _(f'The {store.name} was removed'))
        store.delete()

    @classmethod
    def create_seller_product(cls, data: Dict) -> bool:
        """
        Create new SellerProduct
        """
        if SellerProduct.objects.filter(seller=data['seller'], product=data['product']).exists():
            return False
        else:
            SellerProduct.objects.create(
                seller=data['seller'],
                product=data['product'],
                price=data['price'],
                quantity=data['quantity'])
            return True

    @classmethod
    def edit_seller_product(cls, data: Dict, instance: SellerProduct) -> None:
        """
        Edit SellerProduct instance
        """
        instance.price = data['price']
        instance.quantity = data['quantity']
        instance.save()

    @classmethod
    def get_seller_products(cls, user: User) -> QuerySet:
        """
        Get all products, added by user
        """
        owner_sp_ache_key = 'owner_sp:{}'.format(user.id)
        products = cache.get(owner_sp_ache_key)
        if not products:
            products = SellerProduct.objects.select_related('seller', 'product', 'product__category')\
                                    .filter(seller__owner=user)
            cache.set(owner_sp_ache_key, products, 60 * 60)
        return products

    @classmethod
    def remove_seller_product(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        item = SellerProduct.objects.select_related('seller', 'product').get(id=request.GET.get('id'))
        messages.add_message(request, SUCCESS_DEL_PRODUCT,
                             _(f'Product {item.product.name} from the store {item.seller.name} was removed'))
        item.delete()

    @classmethod
    def get_products(cls, **kwargs) -> QuerySet:
        """
        Get Products by category, Seller instance or get all Products
        """
        if 'category_id' in kwargs.keys():
            return Product.objects.select_related('category').filter(category=kwargs.get('category_id'))
        elif 'instance' in kwargs.keys():
            return Product.objects.select_related('category').filter(seller_products__seller=kwargs.get('instance'))
        else:
            return Product.objects.select_related('category').all()

    @classmethod
    def get_viewed_products(cls, user: User) -> QuerySet:
        """
        Get viewed SellerProducts by user
        """
        viewed_cache_key = 'viewed:{}'.format(user.id)
        viewed = cache.get(viewed_cache_key)
        if not viewed:
            viewed = ViewedProduct.objects.select_related('product__product', 'product__product__category')\
                                          .filter(user=user)\
                                          .order_by('-date')
            cache.set(viewed_cache_key, viewed, 60 * 60)
        return viewed

    @classmethod
    def get_last_order(cls, user: User) -> QuerySet:
        """
        Get last user Order
        """
        last_order_cache_key = 'user_last_order:{}'.format(user.id)
        order = cache.get(last_order_cache_key)
        if not order:
            order = cls.get_all_orders(user=user).last()
            cache.set(last_order_cache_key, order, 60 * 60)
        return order

    @classmethod
    def get_all_orders(cls, user: User) -> QuerySet:
        """
        Get all user Orders
        """
        orders_cache_key = 'user_orders:{}'.format(user.id)
        orders = cache.get(orders_cache_key)
        if not orders:
            orders = Order.objects.filter(customer=user)
            cache.set(orders_cache_key, orders, 60 * 60)
        return orders

    @classmethod
    def request_add_new_product(cls, product: Product, user: User) -> None:
        """
        Create ProductRequest instance
        """
        product.is_published = False
        product.user = user
        product.save()


@receiver(post_delete, sender=Seller)
def delete_IconFile(**kwargs) -> None:
    """
    The signal for removing icon Seller, when the store is deleting
    """
    file = kwargs.get('instance')
    file.icon.delete(save=False)
