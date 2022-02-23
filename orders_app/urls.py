from django.urls import path
from orders_app.views import CartView, ViewedGoodsView, CompareView


app_name = 'orders'
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart_detail'),
    path('add/<int:product_id>/', CartAdd.as_view(), name='cart_add'),
    path('decrease/<int:product_id>/', CartDecreaseQuantity.as_view(), name='cart_decrease'),
    path('increase/<int:product_id>/', CartIncreaseQuantity.as_view(), name='cart_increase'),
    path('remove/<int:product_id>/', CartRemove.as_view(), name='cart_remove'),
    path('clear/', cart_clear, name='cart_clear'),

    path('step1/', OrderStepOne.as_view(), name='order_step_one'),
    path('step2/', OrderStepTwo.as_view(), name='order_step_two'),
    path('step3/', OrderStepThree.as_view(), name='order_step_three'),
    path('step4/', OrderStepFour.as_view(), name='order_step_four'),

    path('payment/<int:order_id>', PaymentView.as_view(), name='payment'),
    path('payment/card/<int:order_id>', PaymentWithCardView.as_view(), name='payment_with_card'),
    path('done/', payment_done, name='payment_done'),
    path('canceled/', payment_canceled, name='payment_canceled'),

    path('viewed/', ViewedGoodsView.as_view(), name='viewed'),
    path('compare/', CompareView.as_view(), name='compare')
]
