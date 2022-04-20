from django import forms
from django.forms import CheckboxInput, FileInput

from goods_app.models import ProductRequest
from stores_app.models import Seller, SellerProduct, ProductImportFile
from django.utils.translation import gettext_lazy as _


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
        fields = ['category', 'name', 'description', 'store', 'notes','image']
        exclude = ['code', 'slug', 'rating', 'is_published', 'tags']


class AddRequestNewProductAdminForm(forms.ModelForm):
    is_published = forms.BooleanField(label='Publishing status', required=False, widget=CheckboxInput())

    class Meta:
        model = ProductRequest
        exclude = ['rating', 'tags']


class ImportForm(forms.ModelForm):
    file = forms.FileField(label=_('Your json file'), required=True, widget=FileInput(attrs={'class': 'import_row',
                                                                                             'accept': '.json',
                                                                                             }))

    class Meta:
        model = ProductImportFile
        fields = ['file', ]
