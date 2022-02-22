from django import forms

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
        fields = ['discount', 'price', 'price_after_discount', 'quantity']
        exclude = ['seller', 'product', ]


class AddRequestNewProduct(forms.Form):
    pass
