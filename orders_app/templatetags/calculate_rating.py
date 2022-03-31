from django import template

register = template.Library()


@register.filter(name='filled_stars')
def filled_stars(rating: int):
    """
    Кастомный фильтр, который позволяет итерироваться
    по значению рейтинга в шаблоне (товары для сравнения)
    """
    if not rating:
        rating = 0
    return range(int(rating))


@register.filter(name='empty_stars')
def empty_stars(rating: int):
    """
    Кастомный фильтр, который позволяет итерироваться
    по значению 5-рейтинг в шаблоне (товары для сравнения)
    """
    if not rating:
        rating = 0
    return range(int(5 - rating))
