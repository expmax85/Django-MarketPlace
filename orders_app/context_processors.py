from orders_app.services import CartService


def cart(request):
    """
    Контекст-процессор корзины для отображения информации по корзине на всех страницах
    """
    cart = CartService(request)
    return {'cart': cart}
