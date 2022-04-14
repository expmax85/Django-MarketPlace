from typing import Callable

from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
from django.views import View

from discounts_app.services import get_discounted_prices_for_seller_products
from profiles_app.forms import RegisterForm, RestorePasswordForm, AccountEditForm
from profiles_app.services import get_user_and_change_password, get_auth_user, reset_phone_format
from orders_app.services.cart import CartService
from stores_app.services import StoreServiceMixin


class UserLogin(LoginView):
    """
    Аутентификация пользователей

    ::Страница: Логин пользователя
    """
    template_name = 'account/login.html'
    success_url = '/'

    def get_success_url(self) -> str:
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)

    def form_valid(self, form: AuthenticationForm) -> HttpResponseRedirect:
        """
        Security check complete. Log the user in.
        Метод переопределен для слияния анонимной корзины
        с корзиной аутентифицированного пользователя
        """
        old_cart = CartService(self.request)
        login(self.request, form.get_user())
        new_cart = CartService(self.request)
        new_cart.merge_carts(old_cart)
        return HttpResponseRedirect(self.get_success_url())


class UserLogout(LogoutView):
    """
    Выход с сайта

    ::Страница: Логаут пользователя
    """
    template_name = 'account/logout.html'
    next_page = '/users/login'


class RegisterView(View):
    """
    Регистрация нового пользователя

    ::Страница: Регистрация пользователей
    """
    def get(self, request: HttpRequest) -> Callable:
        form = RegisterForm()
        return render(request, 'account/signup.html', context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
        """
        Метод переопределен для слияние анонимной корзины
        с корзиной аутентифицированного пользователя
        """
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            old_cart = CartService(self.request)
            user = form.save()
            reset_phone_format(instance=user)
            login(request, get_auth_user(data=form.cleaned_data))
            new_cart = CartService(self.request)
            new_cart.merge_carts(old_cart)
            return redirect('/')
        return render(request, 'account/signup.html', context={'form': form})


class RestorePasswordView(View):
    """
    Представление восстановления пароля

    ::Страница: Восстановление пароля
    """
    def get(self, request: HttpRequest) -> Callable:
        form = RestorePasswordForm()
        return render(request, 'account/password_reset.html', context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
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


class AccountView(LoginRequiredMixin, StoreServiceMixin, View):
    """
    Страница информации об аккаунте

    ::Страница: Аккаунт
    """
    template_name = 'account/account.html'

    def get(self, request: HttpRequest) -> Callable:
        viewed = list(self.get_viewed_products(user=request.user))[-3:]
        if viewed:
            products = get_discounted_prices_for_seller_products(viewed)
        else:
            products = False
        context = {
            'last_order': self.get_last_order(user=request.user),
            'viewed_products': products
        }
        return render(request, 'account/account.html', context=context)


class AccountEditView(LoginRequiredMixin, View):
    """
    Страница редактирования информации об аккаунте

    ::Страница: Аккаунт
    """
    def get(self, request: HttpRequest) -> Callable:
        form = AccountEditForm()
        return render(request, 'account/profile.html', context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
        form = AccountEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            reset_phone_format(instance=user)
            messages.add_message(request, messages.SUCCESS,
                                 _('The profile was saved successfully'))
            return render(request, 'account/profile.html', context={'form': form})
        return render(request, 'account/profile.html', context={'form': form})
