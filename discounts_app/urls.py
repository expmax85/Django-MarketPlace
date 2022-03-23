from django.urls import path
from discounts_app.views import *

app_name = 'discounts'

urlpatterns = [
    path('', DiscountsListView.as_view(), name='discounts-list'),
]
