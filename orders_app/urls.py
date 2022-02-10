from django.urls import path
from orders_app.views import CartView, ViewedGoodsView

app_name = 'orders'
urlpatterns = [
    path('orders/cart/', CartView.as_view(), name='cart'),
    path('orders/viewed/', ViewedGoodsView.as_view(), name='viewed'),
]
