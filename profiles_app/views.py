from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import CreateView
from profiles_app.forms import RegisterForm


class UserLogin(LoginView):
    """
    Logout пользователей
    """
    template_name = 'profiles_app/login.html'
    success_url = '/'

    def get_success_url(self) -> str:
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)


class UserLogout(LogoutView):
    """
    Logout пользователей
    """
    template_name = 'app_users/logout.html'
    next_page = '/users/login'


class RegisterView(CreateView):
    """
    Страница регистрации нового пользователя
    """
    form_class = RegisterForm
    template_name = 'profiles_app/register.html'
    success_url = '/'


