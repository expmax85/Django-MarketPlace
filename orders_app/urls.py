from django.urls import path
from orders_app.views import CartView, ViewedGoodsView


app_name = 'orders'
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('viewed/', ViewedGoodsView.as_view(), name='viewed'),
]
