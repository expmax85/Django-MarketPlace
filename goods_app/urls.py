from django.urls import path
from goods_app.views import index
from goods_app.views import CatalogByCategory

urlpatterns = [
    path('', index, name='index_url'),
    path('catalogs/<slug>/', CatalogByCategory.as_view(), name="catalog_by_category_url"),
]
