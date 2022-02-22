from django import forms
from orders_app.models import Order

# PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    quantity = forms.IntegerField(min_value=1)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderStepOneForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['fio', 'phone', 'email']


class OrderStepTwoForm(forms.ModelForm):
    class Meta:
        model = Order
        widgets = {
            'delivery': forms.RadioSelect(
                attrs={
                    'class': 'toggle-box'
                }
            ),
            # 'payment_method': forms.RadioSelect(
            #     attrs={
            #         'class': 'toggle-box'
            #     }
            # ),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-textarea'
                }
            )
        }
        fields = ['delivery', 'city', 'address']


class OrderStepThreeForm(forms.ModelForm):
    class Meta:
        model = Order
        widgets = {
            'payment_method': forms.RadioSelect(
                attrs={
                    'class': 'toggle-box'
                }
            ),}
        fields = ['payment_method']