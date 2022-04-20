from typing import Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Prefetch
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from discounts_app.models import ProductDiscount, GroupDiscount, CartDiscount
from discounts_app.services import get_discounted_prices_for_seller_products
from orders_app.models import Order, ViewedProduct
from django.conf import settings
from stores_app.models import Seller, SellerProduct
from goods_app.models import Product

User = get_user_model()


class StoreServiceMixin:
    """
    Mixin with functions for queries by models Seller and SellerProduct

    All available methods:
    get_base_products(query params) - get products
    request_add_new_product(product, user)
    get_all_orders(user)
    get_last_order(user)
    get_viewed_products(user) - get all viewed SellerProduct instances
    get_store(slug) - get Seller instance with slug=slug
    get_user_stores(user) - get all Seller models by owner=user
    remove_store(request) - remove Seller instance with id=request.id=request

    create_seller_product(data) - create SelleProduct instance
    edit_seller_product(data, instance) - edit SellerProduct instance
    get_seller_products(user, calculate_prices) - get SellerProducts query by Sellers owner=user
    remove_seller_product(request) - Remove SellerProduct instance with id=request.id

    create_product_discount(user)
    get_product_discounts(user)
    edit_product_group_discount(data, instance)
    remove_product_discount(request)

    create_group_discount(user)
    get_group_discounts(user)
    edit_group_group_discount(data, instance)
    remove_group_discount(request)

    create_cart_discount(user)
    get_cart_discounts(user)
    edit_cart_group_discount(data, instance)
    remove_cart_discount(request)
    """

    @classmethod
    def get_store(cls, slug: str) -> QuerySet:
        """
        Get store with slug

        """
        return Seller.objects.get(slug=slug)

    @classmethod
    def get_all_stores(cls):
        """
        Get all stores
        """
        stores_cache_key = 'stores:all'
        stores = cache.get(stores_cache_key)
        if not stores:
            stores = Seller.objects.all()
            cache.set(stores_cache_key, stores, 24 * 60 * 60)
        return stores

    @classmethod
    def get_user_stores(cls, user: User) -> QuerySet:
        """
        Get all stores by user
        """
        stores_cache_key = 'stores:{}'.format(user.id)
        stores = cache.get(stores_cache_key)
        if not stores:
            stores = Seller.objects.filter(owner=user)
            cache.set(stores_cache_key, stores, 24 * 60 * 60)
        return stores

    @classmethod
    def remove_store(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        store = Seller.objects.get(slug=request.GET.get('id'))
        messages.add_message(request, settings.SUCCESS_DEL_STORE, _(f'The {store.name} was removed'))
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
    def get_seller_products(cls, seller: Seller) -> QuerySet:
        """
        Get all products, added by user
        """
        owner_sp_cache_key = 'seller_sp:{}'.format(seller.id)
        products = cache.get(owner_sp_cache_key)
        if not products:
            products = SellerProduct.objects.select_related('seller', 'product',
                                                            'product__category',
                                                            'product__category__parent') \
                                            .filter(seller=seller)
            cache.set(owner_sp_cache_key, products, 24 * 60 * 60)
        products = get_discounted_prices_for_seller_products(products)
        return products

    @classmethod
    def get_all_owner_products(cls, user: User) -> QuerySet:
        """
        Get all products, added by user
        """
        owner_sp_cache_key = 'owner_sp:{}'.format(user.id)
        products = cache.get(owner_sp_cache_key)
        if not products:
            products = SellerProduct.objects.select_related('seller', 'product',
                                                            'product__category',
                                                            'product__category__parent') \
                                            .filter(seller__owner=user)
            cache.set(owner_sp_cache_key, products, 24 * 60 * 60)
        products = get_discounted_prices_for_seller_products(products)
        return products

    @classmethod
    def remove_seller_product(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        item = SellerProduct.objects.select_related('seller', 'product',
                                                    'product__category',
                                                    'product__category__parent') \
                                    .get(id=request.GET.get('id'))
        messages.add_message(request, settings.SUCCESS_DEL_PRODUCT,
                             _(f'Product {item.product.name} from the store {item.seller.name} was removed'))
        item.delete()

    @classmethod
    def get_base_products(cls, **kwargs) -> QuerySet:
        """
        Get Products by category, Seller instance or get all Products
        """
        if 'category_id' in kwargs.keys():
            products = Product.objects.select_related('category', 'category__parent')\
                                      .filter(category=kwargs.get('category_id'))
        else:
            base_products_cache_key = 'base_products:all'
            products = cache.get(base_products_cache_key)
            if not products:
                products = Product.objects.select_related('category', 'category__parent').all()
                cache.set(base_products_cache_key, products, 24 * 60 * 60)
        return products

    @classmethod
    def get_viewed_products(cls, user: User) -> QuerySet:
        """
        Get viewed SellerProducts by user
        """
        viewed_cache_key = 'viewed:{}'.format(user.id)
        products = cache.get(viewed_cache_key)
        if not products:
            products = SellerProduct.objects.select_related('seller', 'product',
                                                            'product__category',
                                                            'product__category__parent') \
                                            .prefetch_related(Prefetch('viewed_list',
                                                                   queryset=ViewedProduct.objects.filter(user=user))) \
                                            .filter(viewed_list__user=user)
            cache.set(viewed_cache_key, products, 24 * 60 * 60)
        return products

    @classmethod
    def get_last_order(cls, user: User) -> QuerySet:
        """
        Get last user Order
        """
        last_order_cache_key = 'user_last_order:{}'.format(user.id)
        order = cache.get(last_order_cache_key)
        if not order:
            order = cls.get_all_orders(user=user).last()
            cache.set(last_order_cache_key, order, 24 * 60 * 60)
        return order

    @classmethod
    def get_all_orders(cls, user: User) -> QuerySet:
        """
        Get all user Orders
        """
        orders_cache_key = 'user_orders:{}'.format(user.id)
        orders = cache.get(orders_cache_key)
        if not orders:
            orders = Order.objects.filter(customer=user, in_order=True)
            cache.set(orders_cache_key, orders, 24 * 60 * 60)
        return orders

    @classmethod
    def request_add_new_product(cls, product: Product, user: User) -> None:
        """
        Create ProductRequest instance
        """
        product.slug = "_".join([str(product.name) + str(product.category.name)])
        product.is_published = False
        product.user = user
        product.save()

    @classmethod
    def create_product_discount(cls, data: Dict) -> bool:
        """
        Create new ProductDiscount
        """
        seller_products = data['seller_products']
        data.pop('seller_products', None)
        discount = ProductDiscount(**data)
        discount.save()
        discount.seller_products.set(seller_products)
        discount.save()
        return True

    @classmethod
    def get_product_discounts(cls, user: User) -> QuerySet:
        """
        Get all product discounts, added by user
        """
        owner_sd_cache_key = 'owner_product_discounts:{}'.format(user.id)
        product_discounts = cache.get(owner_sd_cache_key)
        if not product_discounts:
            product_discounts = ProductDiscount.objects.filter(seller__owner=user)
            cache.set(owner_sd_cache_key, product_discounts, 24 * 60 * 60)
        return product_discounts

    @classmethod
    def edit_store_product_discount(cls, data: Dict, instance: ProductDiscount) -> None:
        """
        Edit SellerProduct instance
        """
        for attr, value in data.items():
            if attr != 'seller_products':
                setattr(instance, attr, value)
        instance.seller_products.set(data['seller_products'])
        instance.save()

    @classmethod
    def remove_store_product_discount(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        item = ProductDiscount.objects.select_related('seller').get(id=request.GET.get('id'))
        messages.add_message(request, settings.SUCCESS_DEL_PRODUCT_DISCOUNT,
                             _(f'Product discount {item.name} from the store {item.seller.name} was removed'))
        item.delete()

    @classmethod
    def create_group_discount(cls, data: Dict) -> bool:
        """
        Create new ProductDiscount
        """
        discount = GroupDiscount(**data)
        discount.save()
        return True

    @classmethod
    def get_group_discounts(cls, user: User) -> QuerySet:
        """
        Get all product discounts, added by user
        """
        owner_gd_cache_key = 'owner_group_discounts:{}'.format(user.id)
        group_discounts = cache.get(owner_gd_cache_key)
        if not group_discounts:
            group_discounts = GroupDiscount.objects.filter(seller__owner=user)
            cache.set(owner_gd_cache_key, group_discounts, 24 * 60 * 60)
        return group_discounts

    @classmethod
    def edit_store_group_discount(cls, data: Dict, instance: GroupDiscount) -> None:
        """
        Edit SellerProduct instance
        """
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()

    @classmethod
    def remove_store_group_discount(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        item = GroupDiscount.objects.select_related('seller').get(id=request.GET.get('id'))
        messages.add_message(request, settings.SUCCESS_DEL_GROUP_DISCOUNT,
                             _(f'Group discount {item.name} from the store {item.seller.name} was removed'))
        item.delete()

    @classmethod
    def create_cart_discount(cls, data: Dict) -> bool:
        """
        Create new ProductDiscount
        """
        discount = CartDiscount(**data)
        discount.save()
        return True

    @classmethod
    def get_cart_discounts(cls, user: User) -> QuerySet:
        """
        Get all product discounts, added by user
        """
        owner_cd_ache_key = 'owner_card_discounts:{}'.format(user.id)
        cart_discounts = cache.get(owner_cd_ache_key)
        if not cart_discounts:
            cart_discounts = CartDiscount.objects.filter(seller__owner=user)
            cache.set(owner_cd_ache_key, cart_discounts, 60 * 60)
        return cart_discounts

    @classmethod
    def edit_store_cart_discount(cls, data: Dict, instance: CartDiscount) -> None:
        """
        Edit SellerProduct instance
        """
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()

    @classmethod
    def remove_store_cart_discount(cls, request: HttpRequest) -> None:
        """
        Remove store
        """
        item = CartDiscount.objects.select_related('seller').get(id=request.GET.get('id'))
        messages.add_message(request, settings.SUCCESS_DEL_CART_DISCOUNT,
                             _(f'Cart discount {item.name} from the store {item.seller.name} was removed'))
        item.delete()
