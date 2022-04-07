from django import template

register = template.Library()


@register.filter(name='find_errors')
def find_errors(string: str):
    """
    Кастомный фильтр, проверяет наличие errors в строке лога
    """

    if string.find('Error:') != -1:
        return 'Error'
    elif string.find('Warning:') != -1:
        return 'Warning'
    else:
        return 'Success'
