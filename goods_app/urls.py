from django.urls import path
from goods_app.views import *
from goods_app.json_filter import JsonFilterStore


app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index_url'),
    path('product-detail/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),

    path('catalogs/<slug>/sotrby/<str:sort_type>/page/<int:page>',
         CatalogByCategory.as_view(),
         name="catalog_by_category_url"),

    path('catalogs/<slug>/sotrby/<str:sort_type>/page/<int:page>/filter',
         CatalogFilter.as_view(), name='catalog_filter_url'),
    #Альтернативный каталог
    path('catalog/', JsonFilterStore.as_view(), name='json-filter')
]
