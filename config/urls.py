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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from settings_app.views import AdminView

urlpatterns = [
    path('i18n', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('admin/', include('admin_tools.urls')),
    path('api_auth/', include('rest_framework.urls')),
    path('api/', include('payments_app.urls')),
    path('settings-admin/setup/', AdminView.as_view(), name='admin-setup'),
    path('setup-actions/', include('settings_app.urls', namespace='settings-polls')),
    path('', include('goods_app.urls', namespace='goods-polls')),
    path('users/', include('profiles_app.urls', namespace='profiles-polls')),
    path('accounts/', include('allauth.urls')),
    path('orders/', include('orders_app.urls', namespace='orders-polls')),
    path('stores/', include('stores_app.urls', namespace='stores-polls')),
    path('discounts/', include('discounts_app.urls', namespace='discounts-polls')),
    path('__debug__/', include('debug_toolbar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
