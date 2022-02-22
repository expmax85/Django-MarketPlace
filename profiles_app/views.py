from typing import Callable

from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View

from profiles_app.forms import RegisterForm, RestorePasswordForm, AccountEditForm
from profiles_app.services import get_user_and_change_password, get_auth_user, reset_phone_format
from django.utils.translation import gettext_lazy as _


class UserLogin(LoginView):
    """
    Login пользователей
    """
    template_name = 'account/login.html'
    success_url = '/'

    def get_success_url(self) -> str:
        print(self.request)
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
    def get(self, request) -> Callable:
        form = RegisterForm()
        return render(request, 'account/signup.html', context={'form': form})

    def post(self, request) -> Callable:
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            reset_phone_format(instance=user)
            login(request, get_auth_user(data=form.cleaned_data))
            return redirect('/')
        return render(request, 'account/signup.html', context={'form': form})


class RestorePasswordView(View):
    """
    Страница восстановления пароля
    """
    def get(self, request) -> Callable:
        form = RestorePasswordForm()
        return render(request, 'account/password_reset.html', context={'form': form})

    def post(self, request) -> Callable:
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
                return render(request, 'account/password_reset_error.html')
        return render(request, 'account/password_reset.html', context={'form': form})


class AccountView(LoginRequiredMixin, View):
    """
    Информация об аккаунте
    """
    template_name = 'account/account.html'

    def get(self, request) -> Callable:
        return render(request, 'account/account.html')


class AccountEditView(LoginRequiredMixin, View):
    """
    Редактирование профиля
    """
    def get(self, request) -> Callable:
        form = AccountEditForm()
        return render(request, 'account/profile.html', context={'form': form})

    def post(self, request) -> Callable:
        form = AccountEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            reset_phone_format(instance=user)
            messages.add_message(request, messages.SUCCESS,
                                 _('The profile was saved successfully'))
            return render(request, 'account/profile.html', context={'form': form})
        return render(request, 'account/profile.html', context={'form': form})
