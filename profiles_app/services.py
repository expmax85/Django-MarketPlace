import os
from typing import Callable, Union

from django.contrib.auth import get_user_model, authenticate
from django.forms import EmailField
from config.settings import MEDIA_ROOT


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


def remove_old_avatar(file: str) -> None:
    path = os.path.normpath(os.path.join(MEDIA_ROOT, str(file)))
    os.remove(path)
