from django import forms
from goods_app.models import ProductComment


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ['product', 'user', 'author', 'content', 'rating']
        exclude = ['added', ]
