from django.urls import path
from stores_app.views import *

from stores_app.views import AddNewStoreView, AddSellerProductView, SellersRoomView, remove_Store, \
    remove_SellerProduct, EditStoreView, StoreDetailView, EditSelleProductView, RequestNewProduct, CategoryFilter,\
    ImportView

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
    # discount endpoints
    path('add-store-product-discount/', AddProductDiscountView.as_view(), name='add-store-product-discount'),
    path('delete-store-product-discount/', remove_ProductDiscount, name='delete-store-product-discount'),
    path('edit-store-product-discount/<str:slug>/<int:pk>/',
         EditProductDiscountView.as_view(),
         name='edit-store-product-discount'),

    path('add-store-group-discount/', AddGroupDiscountView.as_view(), name='add-store-group-discount'),
    path('delete-store-group-discount/', remove_GroupDiscount, name='delete-store-group-discount'),
    path('edit-store-group-discount/<str:slug>/<int:pk>/',
         EditGroupDiscountView.as_view(),
         name='edit-store-group-discount'),

    path('add-store-cart-discount/', AddCartDiscountView.as_view(), name='add-store-cart-discount'),
    path('delete-store-cart-discount/', remove_CartDiscount, name='delete-store-cart-discount'),
    path('edit-store-cart-discount/<str:slug>/<int:pk>/',
         EditCartDiscountView.as_view(),
         name='edit-store-cart-discount'),
    path('import/', ImportView.as_view(), name='import')
]
