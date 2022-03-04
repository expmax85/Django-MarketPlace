from django.urls import path
from orders_app.views import *


app_name = 'orders'
urlpatterns = [
    # эндпоинты корзины
    path('cart/', CartView.as_view(), name='cart_detail'),
    path('add/<int:product_id>/', CartAdd.as_view(), name='cart_add'),
    path('decrease/<int:product_id>/', CartDecreaseQuantity.as_view(), name='cart_decrease'),
    path('increase/<int:product_id>/', CartIncreaseQuantity.as_view(), name='cart_increase'),
    path('remove/<int:product_id>/', CartRemove.as_view(), name='cart_remove'),
    path('clear/', cart_clear, name='cart_clear'),
    # эндпоинты оформления заказа
    path('step1/', OrderStepOne.as_view(), name='order_step_one'),
    path('step2/', OrderStepTwo.as_view(), name='order_step_two'),
    path('step3/', OrderStepThree.as_view(), name='order_step_three'),
    path('step4/', OrderStepFour.as_view(), name='order_step_four'),
    # эндпоинты оплаты
    path('payment/<int:order_id>', PaymentView.as_view(), name='payment'),
    path('payment/card/<int:order_id>', PaymentWithCardView.as_view(), name='payment_with_card'),
    path('done/', payment_done, name='payment_done'),
    path('canceled/', payment_canceled, name='payment_canceled'),
    # эндпоинты просмотренных товаров
    path('viewed/', ViewedGoodsView.as_view(), name='viewed'),
    # эндпоинты товаров для сравнения
    path('compare/', CompareView.as_view(), name='compare'),
    path('compare/add/<int:product_id>/', AddToCompare.as_view(), name='add-to-compare'),
    path('compare/remove/<str:product_name>/', RemoveFromCompare.as_view(), name='remove-from-compare'),
    # эндпоинты истории заказов
    path('history/', HistoryOrderView.as_view(), name='history-order'),
    path('history/<int:order_id>', HistoryOrderDetail.as_view(), name='history-order-detail')
]
