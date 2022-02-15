from typing import Callable, Union

from django.contrib.auth import get_user_model, authenticate
from django.forms import EmailField


User = get_user_model()


def get_user_and_change_password(email: 'EmailField') -> Union['User', bool]:
    user = User.objects.filter(email=email).first()
    if user:
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        return user
    return False


def get_auth_user(form) -> Callable:
    email = form.cleaned_data['email']
    raw_password = form.cleaned_data['password1']
    return authenticate(email=email, password=raw_password)


def get_customer(user_id: int) -> 'User':
    return User.objects.get(id=user_id)


def edit_user(user_id: int, form) -> None:
    User.objects.filter(id=user_id).update(**form.cleaned_data)
