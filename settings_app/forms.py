from typing import Any

from django.db.models.fields.files import ImageFieldFile
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

    def clean_image(self) -> ImageFieldFile:
        if 'image' in self.image_list:
            image = self.cleaned_data['image']
            check_image_size(image)
            return image

    def clean_icon(self) -> ImageFieldFile:
        if 'icon' in self.image_list:
            icon = self.cleaned_data['icon']
            check_image_size(icon)
            return icon

    def clean_avatar(self) -> ImageFieldFile:
        if 'avatar' in self.image_list:
            avatar = self.cleaned_data['avatar']
            check_image_size(avatar)
            return avatar


class CheckImageIconForm(CheckImageForm):
    """
    Form for checking image file size and resolution icon
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['icon'].help_text = get_help_text(resolution=True)

    def clean_icon(self) -> Any:
        icon = self.cleaned_data['icon']
        check_image_resolution(icon)
        super().clean_icon()
