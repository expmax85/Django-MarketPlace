from orders_app.services import CartService
from orders_app.views import CompareView


def orders_context(request):
    """
    Контекст-процессор корзины для отображения информации по корзине и сравнению товаров на всех страницах
    """

    cart = CartService(request)
    total = CompareView().get_quantity(request)
    return {'cart': cart,
            'total_compared': total}
