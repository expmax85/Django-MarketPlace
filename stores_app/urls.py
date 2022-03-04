from django.urls import path
from stores_app.views import AddNewStoreView, AddSellerProductView, SellersRoomView, remove_Store, \
    remove_SellerProduct, EditStoreView, StoreDetailView, EditSelleProductView, RequestNewProduct, CategoryFilter

app_name = 'stores'
urlpatterns = [
    path('add-store/', AddNewStoreView.as_view(), name='add-store'),
    path('add-store-product/', AddSellerProductView.as_view(), name='add-store-product'),
    path('sellers-room/', SellersRoomView.as_view(), name='sellers-room'),
    path('request-add-new-product/', RequestNewProduct.as_view(), name='request-new-product'),
    path('category-filter/', CategoryFilter.as_view(), name='category-filter'),
    path('delete-store/', remove_Store, name='delete-store'),
    path('delete-seller-product/', remove_SellerProduct, name='delete-seller-product'),
    path('edit-store/<str:slug>/', EditStoreView.as_view(), name='edit-store'),
    path('store-detail/<str:slug>/', StoreDetailView.as_view(), name='store-detail'),
    path('<str:slug>/<int:pk>/', EditSelleProductView.as_view(), name='edit-seller-product'),
]
