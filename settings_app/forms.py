from typing import List

from django.forms import ModelForm, ImageField
from django.utils.translation import gettext_lazy as _

from settings_app.utils import check_image_size, check_image_resolution, get_help_text


class CheckImageForm(ModelForm):
    """
    Form for checking image file size
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.image_list = []
        for field_name, value in self.fields.items():
            if isinstance(value, ImageField):
                self.image_list.append(field_name)
        if not self.image_list:
            raise ValueError(_('Image field does not exist'))
        for field in self.image_list:
            self.fields[str(field)].help_text = get_help_text(size=True)

    def clean_image(self) -> List:
        for field in self.image_list:
            image = self.cleaned_data[str(field)]
            check_image_size(image)
        return self.image_list


class CheckImageIconForm(CheckImageForm):
    """
    Form for checking image file size and resolution icon
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['icon'].help_text = get_help_text(resolution=True)

    def clean_image(self) -> List:
        image_list = super().clean_image()
        if 'icon' in image_list:
            i = image_list.index('icon')
            field = image_list[i]
            image = self.cleaned_data[str(field)]
            check_image_resolution(image)
        return image_list
