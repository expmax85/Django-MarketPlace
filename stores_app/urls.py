from django.urls import path
from stores_app.views import *


app_name = 'stores'
urlpatterns = [
    path('add-store/', AddNewStoreView.as_view(), name='add-store'),
    path('add-store-product/', AddSellerProductView.as_view(), name='add-store-product'),
    path('sellers-room/', SellersRoomView.as_view(), name='sellers-room'),
    path('delete-store/', remove_Store, name='delete-store'),
    path('delete-seller-product/', remove_SellerProduct, name='delete-seller-product'),
    path('edit-store/<str:slug>/', EditStoreView.as_view(), name='edit-store'),
    path('store-detail/<str:slug>/', StoreDetailView.as_view(), name='store-detail'),
    path('<str:slug>/<int:pk>/', EditSelleProductView.as_view(), name='edit-seller-product'),
]
