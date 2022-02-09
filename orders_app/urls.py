from django.urls import path
from orders_app.views import CartView, ViewedGoodsView

urlpatterns = [
    path('cart', CartView.as_view(), name='cart'),
    path('viewed', ViewedGoodsView.as_view(), name='viewed'),
]
