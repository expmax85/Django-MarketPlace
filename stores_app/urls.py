from django.urls import path
from stores_app import views


app_name = 'stores'
urlpatterns = [
    path('add-store/', views.AddNewStoreView.as_view(), name='add-store'),
    path('add-store-product/', views.AddSellerProductView.as_view(), name='add-store-product'),
    path('sellers-room/', views.SellersRoomView.as_view(), name='sellers-room'),
    path('request-add-new-product/', views.RequestNewProduct.as_view(), name='request-new-product'),
    path('category-filter/', views.CategoryFilter.as_view(), name='category-filter'),
    path('delete-store/', views.remove_Store, name='delete-store'),
    path('delete-seller-product/', views.remove_SellerProduct, name='delete-seller-product'),
    path('edit-store/<str:slug>/', views.EditStoreView.as_view(), name='edit-store'),
    path('stores-list/', views.StoresListView.as_view(), name='stores-list'),
    path('products-list/', views.AllSellerProductView.as_view(), name='all-products-list'),
    path('store-detail/<str:slug>/', views.StoreDetailView.as_view(), name='store-detail'),
    path('<str:slug>/<int:pk>/', views.EditSelleProductView.as_view(), name='edit-seller-product'),
    # discount endpoints
    path('add-store-product-discount/', views.AddProductDiscountView.as_view(), name='add-store-product-discount'),
    path('delete-store-product-discount/', views.remove_ProductDiscount, name='delete-store-product-discount'),
    path('edit-store-product-discount/<str:slug>/<int:pk>/',
         views.EditProductDiscountView.as_view(),
         name='edit-store-product-discount'),

    path('add-store-group-discount/', views.AddGroupDiscountView.as_view(), name='add-store-group-discount'),
    path('delete-store-group-discount/', views.remove_GroupDiscount, name='delete-store-group-discount'),
    path('edit-store-group-discount/<str:slug>/<int:pk>/',
         views.EditGroupDiscountView.as_view(),
         name='edit-store-group-discount'),

    path('add-store-cart-discount/', views.AddCartDiscountView.as_view(), name='add-store-cart-discount'),
    path('delete-store-cart-discount/', views.remove_CartDiscount, name='delete-store-cart-discount'),
    path('edit-store-cart-discount/<str:slug>/<int:pk>/',
         views.EditCartDiscountView.as_view(),
         name='edit-store-cart-discount'),
    path('import/', views.ImportView.as_view(), name='import')
]
