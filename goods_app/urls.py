from django.urls import path
from goods_app.views import index
from goods_app.views import CatalogByCategory, CatalogFilter

urlpatterns = [
    path('', index, name='index_url'),

    path('catalogs/<slug>/sotrby/<str:sort_type>/page/<int:page>',
         CatalogByCategory.as_view(),
         name="catalog_by_category_url"),

    path('catalogs/<slug>/sotrby/<str:sort_type>/page/<int:page>/filter',
         CatalogFilter.as_view(), name='catalog_filter_url'),
]
