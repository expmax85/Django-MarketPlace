from django.shortcuts import get_object_or_404
from orders_app.models import Order
from django.http.response import Http404
from payments_app.models import PaymentRequest


def process_payment(order_id: int, account: str) -> bool:
    """
    Функция обработки заявки на оплату
    В случае, если заказ существует и не оплачен, создается запрос в БД на оплату
    """
    try:
        order = get_object_or_404(Order, id=order_id)
        if order:
            if order.in_order and not order.paid:
                PaymentRequest.objects.create(order=order_id,
                                              account=account)
                return True
        return False

    except (IndexError, KeyError, ValueError, Http404):
        return False


def check_status(order_id: int) -> str:
    """
    Функция проверки статуса заказа
    """
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
