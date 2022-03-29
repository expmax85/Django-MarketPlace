from django.shortcuts import get_object_or_404
from orders_app.models import Order


def process_payment(order_id: int, account: str):
    order = get_object_or_404(Order, id=order_id)
    try:
        if int(account) % 2 == 0 and account[-1] != '0' and len(account) == 8 and not order.paid:
            order.paid = True
            order.braintree_id = account
            order.save()
            return True
        return False

    except TypeError:
        return False


def check_status(order_id: int):
    order = get_object_or_404(Order, id=order_id)
    if order:
        if order.in_order is True:
            if order.paid is True:
                return 'Paid'
            else:
                return 'Not Paid'
        return f'No order No {order_id}'
    return f'No order No {order_id}'
