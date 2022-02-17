from django.urls import path
from stores_app.views import *


app_name = 'stores'
urlpatterns = [
    path('add-store/', AddNewStoreView.as_view(), name='add-store'),
    path('add-store-product/', AddSellerProduct.as_view(), name='add-store-product'),
    path('sellers-room/', SellersRoomView.as_view(), name='sellers-room'),
    path('delete-store/', RemoveStoreView.as_view(), name='delete-store'),
    path('delete-seller-product/', RemoveSellerProductView.as_view(), name='delete-seller-product'),
    path('<str:slug>/', StoreDetailView.as_view(), name='store_detail'),
]
