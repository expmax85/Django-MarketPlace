from django.urls import path
from stores_app.views import *


app_name = 'stores'
urlpatterns = [
    path('add-store/', AddNewStoreView.as_view(), name='add-store'),
    path('sellers-room/', SellersRoomView.as_view(), name='sellers-room'),
    path('<str:slug>/', StoreDetailView.as_view(), name='store_detail'),
]
