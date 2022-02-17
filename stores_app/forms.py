from django import forms

from stores_app.models import Seller, SellerProduct


class AddStoreForm(forms.ModelForm):

    class Meta:
        model = Seller
        fields = ['name', 'description', 'address', 'slug', 'email', 'phone', 'icon']
        exclude = ['owner']


class EditStoreForm(forms.ModelForm):

    class Meta:
        model = Seller
        fields = ['name', 'description', 'address', 'email', 'phone', 'icon']
        exclude = ['owner', 'slug']


class AddSellerProductForm(forms.ModelForm):

    class Meta:
        model = SellerProduct
        fields = '__all__'


class AddRequestNewProduct(forms.Form):
    pass
