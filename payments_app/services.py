from django.shortcuts import get_object_or_404
from orders_app.models import Order
from django.http.response import Http404


def process_payment(order_id: int, account: str):
    try:
        order = get_object_or_404(Order, id=order_id)

        if int(account) % 2 == 0 and account[-1] != '0' and len(account) == 8 and not order.paid:
            order.paid = True
            order.braintree_id = account
            order.save()
            return True
        return False

    except (IndexError, KeyError, ValueError, Http404):
        return False


def check_status(order_id: int):
    try:
        order = get_object_or_404(Order, id=order_id)
        if order:
            if order.in_order is True:
                if order.paid is True:
                    return 'Paid'
                else:
                    return 'Not Paid'
        return f'No order No {order_id}'

    except (IndexError, KeyError, Http404):
        return f'No order No {order_id}'

    except ValueError:
        return 'Order number is incorrect'
