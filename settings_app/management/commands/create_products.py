import random

from django.core.management.base import BaseCommand
from stores_app.models import SellerProduct, Seller
from goods_app.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        last = SellerProduct.objects.last()
        sellers = list(Seller.objects.values_list('id', flat=True))
        products = list(Product.objects.values_list('id', flat=True))
        SellerProduct.objects.bulk_create([
                                SellerProduct(product_id=random.choice(products),
                                              seller_id=random.choice(sellers),
                                              price=random.randrange(20, 500, 20),
                                              quantity=random.randrange(1, 30, 1))
                                              for _ in range(int(last.id) + 1, 100)
                                    ])
        self.stdout.write(self.style.SUCCESS('Successfully added 100 products'))
