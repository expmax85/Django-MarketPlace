from django.urls import path
from orders_app import views

app_name = 'orders'
urlpatterns = [
    # эндпоинты корзины
    path('cart/', views.CartView.as_view(), name='cart_detail'),
    path('cart/<int:product_id>', views.CartView.as_view(), name='cart_detail_post'),
    path('add/<int:product_id>/', views.CartAdd.as_view(), name='cart_add'),
    path('add/<int:product_id>/', views.CartAdd.as_view(), name='cart_add_many'),
    path('remove/<int:product_id>/', views.CartRemove.as_view(), name='cart_remove'),
    path('clear/', views.cart_clear, name='cart_clear'),
    # эндпоинты оформления заказа
    path('step1/', views.OrderStepOne.as_view(), name='order_step_one'),
    path('step11/', views.OrderStepOneAnonym.as_view(), name='order_step_one_anonymous'),
    path('step2/', views.OrderStepTwo.as_view(), name='order_step_two'),
    path('step3/', views.OrderStepThree.as_view(), name='order_step_three'),
    path('step4/', views.OrderStepFour.as_view(), name='order_step_four'),
    # эндпоинты оплаты
    path('payment/<int:order_id>', views.PaymentView.as_view(), name='payment'),
    path('payment/card/<int:order_id>', views.PaymentWithCardView.as_view(), name='payment_with_card'),
    path('payment/account/<int:order_id>', views.PaymentWithAccountView.as_view(), name='payment_with_account'),
    path('done/', views.payment_done, name='payment_done'),
    path('canceled/', views.payment_canceled, name='payment_canceled'),
    # эндпоинты товаров для сравнения
    path('compare/', views.CompareView.as_view(), name='compare'),
    path('compare/add/<int:product_id>/', views.AddToCompare.as_view(), name='add-to-compare'),
    path('compare/remove/<str:product_name>/', views.RemoveFromCompare.as_view(), name='remove-from-compare'),
    # эндпоинты истории заказов
    path('history/', views.HistoryOrderView.as_view(), name='history-order'),
    path('history/<int:order_id>', views.HistoryOrderDetail.as_view(), name='history-order-detail'),
    # эндроинты истории просмотров
    path('viewed_history/', views.ViewedGoodsView.as_view(), name='history-view'),
    path('add_viewed/', views.add_viewed, name='add_viewed')
]
