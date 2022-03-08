from django.urls import path
from profiles_app.views import UserLogin, UserLogout, RegisterView, \
    RestorePasswordView, AccountView, AccountEditView

app_name = 'profiles'
urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('restore-password/', RestorePasswordView.as_view(), name='restore-password'),
    path('private-room/', AccountView.as_view(), name='private-room'),
    path('private-room/profile/', AccountEditView.as_view(), name='account-edit'),
]
