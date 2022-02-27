from django.urls import path

from banners_app.adminview import AdminView

urlpatterns = [
    path('settings-admin/setup/', AdminView.as_view(), name='admin-setup'),
    ]
