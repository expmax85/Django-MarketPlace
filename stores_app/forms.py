from django import forms

from stores_app.models import Seller


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
