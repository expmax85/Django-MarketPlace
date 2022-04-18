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
from settings_app.language import set_language

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="MEGANO payment API",
      default_version='v1',
      description="This api is used for getting payments through random account",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="megano@megano.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('i18n', set_language, name='set_language'),
    path('admin/', admin.site.urls),
    path('admin/', include('admin_tools.urls')),
    path('api_auth/', include('rest_framework.urls')),
    path('api/', include('payments_app.urls')),
    path('settings-admin/', include('settings_app.urls', namespace='settings-polls')),
    path('', include('goods_app.urls', namespace='goods-polls')),
    path('users/', include('profiles_app.urls', namespace='profiles-polls')),
    path('accounts/', include('allauth.urls')),
    path('orders/', include('orders_app.urls', namespace='orders-polls')),
    path('stores/', include('stores_app.urls', namespace='stores-polls')),
    path('discounts/', include('discounts_app.urls', namespace='discounts-polls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
