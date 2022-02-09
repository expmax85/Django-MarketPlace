from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from profiles_app.forms import RegisterForm, RestorePasswordForm
from profiles_app.services import get_user_and_change_password, get_auth_user
from django.utils.translation import gettext_lazy as _


class UserLogin(LoginView):
    """
    Login пользователей
    """
    template_name = 'account/login.html'
    success_url = '/'

    def get_success_url(self) -> str:
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)


class UserLogout(LogoutView):
    """
    Logout пользователей
    """
    template_name = 'account/logout.html'
    next_page = '/users/login'


class RegisterView(View):
    """
    Страница регистрации нового пользователя
    """

    def get(self, request):
        form = RegisterForm()
        return render(request, 'account/signup.html', context={'form': form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            login(request, get_auth_user(form))
            return redirect('/')
        return render(request, 'account/signup.html', context={'form': form})


class RestorePasswordView(View):
    """
    Страница восстановления пароля
    """

    def get(self, request):
        form = RestorePasswordForm()
        return render(request, 'account/password_reset.html', context={'form': form})

    def post(self, request):
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_and_change_password(email=email)
            if user:
                send_mail(subject='Restore Password',
                          message='Test',
                          from_email='admin@example.com',
                          recipient_list=[email])
                return render(request, 'account/password_reset_done.html', context={'form': form})
            else:
                return HttpResponse(_('The user with this email is not registered'))
        return render(request, 'account/password_reset.html', context={'form': form})
