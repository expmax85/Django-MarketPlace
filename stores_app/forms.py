from django import forms
from django.forms import CheckboxInput

from goods_app.models import ProductRequest
from stores_app.models import Seller, SellerProduct


class AddStoreForm(forms.ModelForm):

    class Meta:
        model = Seller
        fields = '__all__'


class EditStoreForm(forms.ModelForm):

    class Meta:
        model = Seller
        fields = ['name', 'description', 'address', 'email', 'phone', 'icon']
        exclude = ['owner', 'slug']


class AddSellerProductForm(forms.ModelForm):

    class Meta:
        model = SellerProduct
        fields = '__all__'


class EditSellerProductForm(forms.ModelForm):

    class Meta:
        model = SellerProduct
        fields = ['price', 'quantity']
        exclude = ['seller', 'product', ]


class AddRequestNewProduct(forms.ModelForm):

    class Meta:
        model = ProductRequest
        fields = ['category', 'name', 'description', 'store', 'notes']
        exclude = ['code', 'slug', 'image', 'average_price', 'rating', 'is_published', 'tags']


class AddRequestNewProductAdminForm(forms.ModelForm):
    is_published = forms.BooleanField(label='Publishing status', required=False, widget=CheckboxInput())

    class Meta:
        model = ProductRequest
        exclude = ['rating', 'average_price', 'tags']
