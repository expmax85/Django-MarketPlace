from orders_app.services import CartService


def cart(request):
    cart = CartService(request)
    return {'cart': cart}
