from django.urls import path
from goods_app.views import IndexView, ProductDetailView, get_reviews, post_review, CatalogByCategory, CardForAjax

app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index_url'),
    path('product-detail/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('get_reviews/', get_reviews, name='get_reviews'),
    path('post_review/', post_review, name='post_review'),
    path('limited_deal/', post_review, name='limited-deal'),

    path('catalogs/<slug>/',
         CatalogByCategory.as_view(),
         name="catalog_by_category_url"),

    path('ajax/<slug>/sotrby/<str:sort_type>/page/<int:page>',
         CardForAjax.as_view(), name='ajax')
]
