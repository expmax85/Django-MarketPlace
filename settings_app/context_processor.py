from config.settings import CREATE_PRODUCT_ERROR, SUCCESS_DEL_STORE, SUCCESS_DEL_PRODUCT, SUCCESS_OPTIONS_ACTIVATE, \
    SEND_PRODUCT_REQUEST
from orders_app.services import CartService
from orders_app.views import CompareView


def custom_context(request):

    cart = CartService(request)
    total = CompareView().get_quantity(request)
    return {
        'SUCCESS_OPTIONS_ACTIVATE': SUCCESS_OPTIONS_ACTIVATE,
        'SEND_PRODUCT_REQUEST': SEND_PRODUCT_REQUEST,
        'CREATE_PRODUCT_ERROR': CREATE_PRODUCT_ERROR,
        'SUCCESS_DEL_STORE': SUCCESS_DEL_STORE,
        'SUCCESS_DEL_PRODUCT': SUCCESS_DEL_PRODUCT,
        'cart': cart,
        'total_compared': total
    }
