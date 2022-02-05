from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django import forms


User = get_user_model()


class RegisterForm(UserCreationForm):
    city = forms.CharField(max_length=40, required=False)
    address = forms.CharField(max_length=500, required=False)
    avatar = forms.ImageField(required=False)


    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone',
        ]
        field_classes = {'email': UsernameField}


class RestorePasswordForm(forms.Form):
    email = forms.EmailField(max_length=50, label="E-mail:")
