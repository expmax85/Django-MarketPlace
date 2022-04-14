from django.urls import path
from goods_app.views import IndexView, ProductDetailView, get_reviews, post_review, \
    FullCatalogView, AllCardForAjax

app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index_url'),
    path('product-detail/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('get_reviews/', get_reviews, name='get_reviews'),
    path('post_review/', post_review, name='post_review'),

    path('catalogs/', FullCatalogView.as_view(), name="catalog_url"),

    path('async_catalog/', AllCardForAjax.as_view(), name="ajax_full"),
]
