from django.urls import path
from payments_app.views import payment_view


urlpatterns = [
    path('account_payment/', payment_view, name='account-payment'),
]
