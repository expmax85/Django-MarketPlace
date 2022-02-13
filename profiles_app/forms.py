from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField, UserCreationForm
from django import forms


User = get_user_model()


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone',
            'city', 'avatar', 'address',
        ]
        field_classes = {'email': UsernameField}


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'city', 'avatar', 'address',
        ]


class RestorePasswordForm(forms.Form):
    email = forms.EmailField(max_length=50, required=True)
