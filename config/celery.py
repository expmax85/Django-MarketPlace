from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
# from payments_app.tasks import payment_processor

# from payments_app.models import PaymentRequest
# from orders_app.models import Order


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(['payments_app', ])

# task =app.task
#
#

@app.on_after_configure.connect
def set_periodic(sender, **kwrags) -> None:
    """
    Функция запуска периодической задачи
    :param sender:
    :param kwrags:
    """
    sender.add_periodic_task(
        crontab(),
        check_payments.s()
        # fill_db.s()
    )


@app.task
def check_payments() -> None:
    """
    Функция ежедневного добавления строки записи обменных курсов в БД.
    """
    # payment_processor()
    # print('Something')
    from payments_app.models import PaymentRequest
    from orders_app.models import Order

    payment_requests = PaymentRequest.objects.all()
    for r in payment_requests:
        order = Order.objects.get(id=int(r.order))
        print(order)
        print(r.account)
        if r.account % 2 == 0 and str(r.account)[-1] != '0' and len(str(r.account)) == 8:
            print('checking here')
            print(str(r.account)[-1])
            order.paid = True
            order.braintree_id = r.account
        else:
            order.payment_error = 'Account number is invalid'
        order.save()
        r.delete()
