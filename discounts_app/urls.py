from django.urls import path
from discounts_app.views import DiscountsListView, DiscountDetailView

app_name = 'discounts'

urlpatterns = [
    path('', DiscountsListView.as_view(), name='discounts-list'),
    path('discount-detail/<str:slug>/<int:id>', DiscountDetailView.as_view(), name='discount-detail'),
]
