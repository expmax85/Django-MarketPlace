"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from settings_app import views

app_name = 'settings_app'
urlpatterns = [
    path('clear-all-cache/', views.clear_all_cache, name='clear-all-cache'),
    path('clear-review-cache/', views.clear_review_cache, name='clear-review-cache'),
    path('clear_catalog_cache/', views.clear_catalog_cache, name='clear-catalog-cache'),
    path('clear_banner_cache/', views.clear_banner_cache, name='clear-banner-cache'),
    path('clear_detail_products_cache/', views.clear_detail_products_cache, name='clear-detail-products-cache'),
    path('clear_sellers_cache/', views.clear_sellers_cache, name='clear-sellers-cache'),
    path('clear_users_cache/', views.clear_users_cache, name='clear-users-cache'),

    path('setup/', views.AdminView.as_view(), name='admin-setup'),
    path('update-limited-deal/', views.change_limited_deal, name='manual-change-product'),
    path('update-expire/', views.update_expire, name='manual-expire-change'),
    path('set-end-time/', views.set_expire, name='set-end-time')
]
