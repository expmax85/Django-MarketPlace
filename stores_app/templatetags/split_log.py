from django import template

register = template.Library()


@register.filter(name='split_log')
def split_log(log: str):
    """
    Кастомный фильтр, разбивает лог на строки
    """

    return log.split('>')
