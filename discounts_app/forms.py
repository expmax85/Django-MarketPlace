from django import forms
from discounts_app.models import ProductDiscount, GroupDiscount, CartDiscount
from django.contrib.admin import widgets


class AddProductDiscountForm(forms.ModelForm):

    class Meta:
        model = ProductDiscount
        fields = '__all__'
        widgets = {
            'valid_from': widgets.AdminDateWidget,
            'valid_to': widgets.AdminDateWidget
        }


class AddGroupDiscountForm(forms.ModelForm):

    class Meta:
        model = GroupDiscount
        fields = '__all__'
        widgets = {
            'valid_from': widgets.AdminDateWidget,
            'valid_to': widgets.AdminDateWidget
        }


class AddCartDiscountForm(forms.ModelForm):

    class Meta:
        model = CartDiscount
        fields = '__all__'
        widgets = {
            'valid_from': widgets.AdminDateWidget,
            'valid_to': widgets.AdminDateWidget
        }
