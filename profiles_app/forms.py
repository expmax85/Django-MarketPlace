import re

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class RegisterForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
    # city = forms.CharField(max_length=40, required=False)
    # address = forms.CharField(max_length=500, required=False)
    # avatar = forms.ImageField(required=False)
    phone_valid = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=' '.join([str(_('Phone number must be entered in the format:')), '+999999999',
                                                   str(_('Up to 15 digits allowed.'))]))
    phone = forms.CharField(max_length=17, validators=[phone_valid], required=True)

    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone', 'city', 'avatar', 'address',
        ]
        field_classes = {'email': UsernameField}

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError('jib,rf')
        return phone




class RestorePasswordForm(forms.Form):
    email = forms.EmailField(max_length=50, label="E-mail:")
