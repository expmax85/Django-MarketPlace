from django.urls import path
from profiles_app.views import *


app_name = 'users'
urlpatterns = [
    path('users/login/', UserLogin.as_view(), name='login'),
    path('users/logout/', UserLogout.as_view(), name='logout'),
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/restore_password/', RestorePasswordView.as_view(), name='restore_password'),
    path('users/privateroom/', AccountView.as_view(), name='private_room'),
    path('users/profile/', AccountEditView.as_view(), name='account_edit'),
]
