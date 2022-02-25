import os
from typing import Callable, Union, Dict

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


def get_auth_user(data: Dict) -> Callable:
    email = data['email']
    raw_password = data['password1']
    return authenticate(email=email, password=raw_password)


def remove_old_files(file: str) -> None:
    path = os.path.normpath(os.path.join(MEDIA_ROOT, str(file)))
    if os.path.exists(path) and file:
        os.remove(path)


def reset_phone_format(instance: 'User') -> None:
    try:
        instance.phone = instance.phone[3:].replace(')', '').replace('-', '')
        instance.save(update_fields=['phone'])
    except AttributeError:
        pass
