from orders_app.services import CartService
from orders_app.views import CompareView


def cart(request):
    """
    Контекст-процессор корзины для отображения информации по корзине на всех страницах
    """

    cart = CartService(request)
    return {'cart': cart}

def compare(request):
    """
    Контекст-процессор для отображения количества товаров в списке для сравнения
    """

    total = CompareView().get_quantity(request)
    return {'total_compared': total}
