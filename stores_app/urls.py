from django.urls import path
from stores_app.views import *


app_name = 'stores'
urlpatterns = [
    path('add-store/', AddNewStoreView.as_view(), name='add-store'),
    path('add-store-product/', AddSellerProductView.as_view(), name='add-store-product'),
    path('sellers-room/', SellersRoomView.as_view(), name='sellers-room'),
    path('delete-store/', remove_Store, name='delete-store'),
    path('delete-seller-product/', remove_SellerProduct, name='delete-seller-product'),
    path('<str:slug>/', StoreDetailView.as_view(), name='store_detail'),
    path('<str:store>/<str:slug>/', SelleProductDetailView.as_view(), name='seller-product-detail'),
]
