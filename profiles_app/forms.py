from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone',
            'address', 'city', 'avatar',
        ]