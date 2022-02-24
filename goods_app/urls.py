from django.urls import path
from goods_app.views import index


app_name = 'goods'

urlpatterns = [
    path('', index, name='index_url'),
]
