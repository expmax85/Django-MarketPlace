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

from settings_app.views import clear_all_cache, change_limited_deal, update_expire, set_expire, clear_review_cache

app_name = 'settings_app'
urlpatterns = [
    path('clear-all-cache/', clear_all_cache, name='clear-all-cache'),
    path('clear-review-cache/', clear_review_cache, name='clear-review-cache'),
    path('update-limited-deal/', change_limited_deal, name='manual-change-product'),
    path('update-expire/', update_expire, name='manual-expire-change'),
    path('set-end-time/', set_expire, name='set-end-time')
]