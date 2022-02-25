from django.urls import path
from goods_app.views import *


app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index_url'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail')
]
