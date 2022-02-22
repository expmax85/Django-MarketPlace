from django.shortcuts import render
from django.views import View

from banners_app.services import banner
from goods_app.services import get_all_product_categories
from goods_app.models import ProductCategory


def index(request):
    banners = banner()
    categories = get_all_product_categories()

    return render(request, 'index.html', {'banners': banners, 'categories': categories})


class CatalogByCategory(View):
    """view to get a catalog for a specific category"""

    def get(self, request, slug):
        category = ProductCategory.objects.prefetch_related('products', 'products__seller_products').get(slug=slug)
        categoties = ProductCategory.objects.all()
        # category = ProductCategory.objects.get(slug=slug)
        return render(request, 'goods_app/catalog.html', context={'category': category, 'categories': categoties})
