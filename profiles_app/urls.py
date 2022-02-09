from django.urls import path, include
from profiles_app.views import *


urlpatterns = [
    path('users/login/', UserLogin.as_view(), name='login'),
    path('users/logout/', UserLogout.as_view(), name='logout'),
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/restore_password/', RestorePasswordView.as_view(), name='restore_password'),
    path('accounts/', include('allauth.urls')),
]