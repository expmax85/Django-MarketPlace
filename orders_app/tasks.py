import datetime

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
        crontab(minute="*/10"),
        clear_unpaid_orders.s()
    )


@app.task
def clear_unpaid_orders() -> None:
    """
    Функция очистки просроченных неоплаченных товаров
    """
    from orders_app.models import Order

    time = datetime.datetime.now() - datetime.timedelta(minutes=5)
    orders_to_clear = Order.objects.prefetch_related('order_products', 'order_products__seller_product').\
        filter(ordered__lte=time, in_order=True, paid=False)

    for order in orders_to_clear:
        order_products = order.order_products.all()
        for o_p in order_products:
            o_p.seller_product.quantity += o_p.quantity
            o_p.seller_product.save()

    orders_to_clear.delete()
