from django.forms import ModelForm

from settings_app.utils import check_image_size, check_image_rezolution, get_help_text


class CheckImageIconForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = get_help_text(size=True)
        self.fields['icon'].help_text = get_help_text(rezolution=True)

    def clean_image(self) -> str:
        image = self.cleaned_data['image']
        check_image_size(image)
        return image

    def clean_icon(self) -> str:
        image = self.cleaned_data['icon']
        check_image_size(image)
        check_image_rezolution(image)
        return image


class CheckImageForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            self.fields['image'].help_text = get_help_text(size=True)
        except KeyError:
            self.fields['icon'].help_text = get_help_text(size=True)

    def clean_image(self) -> str:
        try:
            image = self.cleaned_data['image']
        except KeyError:
            image = self.cleaned_data['icon']
        check_image_size(image)
        return image
