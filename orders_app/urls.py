from django.urls import path
from orders_app.views import *

app_name = 'orders'
urlpatterns = [
    # эндпоинты корзины
    path('cart/', CartView.as_view(), name='cart_detail'),
    path('cart/<product_id>', CartView.as_view(), name='cart_detail_post'),
    path('add/<int:product_id>/', CartAdd.as_view(), name='cart_add'),
    path('remove/<int:product_id>/', CartRemove.as_view(), name='cart_remove'),
    path('clear/', cart_clear, name='cart_clear'),
    # эндпоинты оформления заказа
    path('step1/', OrderStepOne.as_view(), name='order_step_one'),
    path('step11/', OrderStepOneAnonym.as_view(), name='order_step_one_anonymous'),
    path('step2/', OrderStepTwo.as_view(), name='order_step_two'),
    path('step3/', OrderStepThree.as_view(), name='order_step_three'),
    path('step4/', OrderStepFour.as_view(), name='order_step_four'),
    # эндпоинты оплаты
    path('payment/<int:order_id>', PaymentView.as_view(), name='payment'),
    path('payment/card/<int:order_id>', PaymentWithCardView.as_view(), name='payment_with_card'),
    path('payment/account/<int:order_id>', PaymentWithAccountView.as_view(), name='payment_with_account'),
    path('done/', payment_done, name='payment_done'),
    path('canceled/', payment_canceled, name='payment_canceled'),
    # эндпоинты товаров для сравнения
    path('compare/', CompareView.as_view(), name='compare'),
    path('compare/add/<int:product_id>/', AddToCompare.as_view(), name='add-to-compare'),
    path('compare/remove/<str:product_name>/', RemoveFromCompare.as_view(), name='remove-from-compare'),
    # эндпоинты истории заказов
    path('history/', HistoryOrderView.as_view(), name='history-order'),
    path('history/<int:order_id>', HistoryOrderDetail.as_view(), name='history-order-detail'),
    # эндроинты истории просмотров
    path('viewed_history/', ViewedGoodsView.as_view(), name='history-view'),
    path('add_viewed/', add_viewed, name='add_viewed')
]
