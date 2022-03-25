from typing import Callable, Union, Dict

from django.contrib.auth import get_user_model, authenticate
from django.forms import EmailField


User = get_user_model()


def get_user_and_change_password(email: 'EmailField') -> Union['User', bool]:
    """
    Function for changing password when it need to restore
    """
    user = User.objects.filter(email=email).first()
    if user:
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        return user
    return False


def get_auth_user(data: Dict) -> Callable:
    """
    Authentication user
    """
    email = data['email']
    raw_password = data['password1']
    return authenticate(email=email, password=raw_password)


def reset_phone_format(instance: 'User') -> None:
    """
    Reset phone format
    """
    try:
        instance.phone = instance.phone[3:].replace(')', '').replace('-', '')
        instance.save(update_fields=['phone'])
    except AttributeError:
        pass
