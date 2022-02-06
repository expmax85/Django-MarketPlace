from django.urls import path
from goods_app.views import index

urlpatterns = [
    path('', index, name='index_url'),
]
