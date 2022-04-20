from celery.schedules import crontab
from config.celery import app


@app.on_after_configure.connect
def set_periodic(sender, **kwrags) -> None:
    """
    Функция запуска периодической задачи
    :param sender:
    :param kwrags:
    """
    sender.add_periodic_task(
        crontab(minute="*/2"),
        check_payments.s()
    )


@app.task
def check_payments() -> None:
    """
    Функция проверки заявок на оплату и изменения статуса заказа на Оплачен, если счёт валиден
    """
    from payments_app.models import PaymentRequest
    from orders_app.models import Order

    payment_requests = PaymentRequest.objects.all()
    for r in payment_requests:
        order = Order.objects.get(id=r.order)
        if r.account % 2 == 0 and str(r.account)[-1] != '0' and len(str(r.account)) == 8:
            order.paid = True
            order.braintree_id = r.account
            order.payment_error = ''
        else:
            order.payment_error = 'Account number is invalid'
        order.save()
    payment_requests.delete()
