# from celery.schedules import crontab
# from config.celery import app
# # from payments_app.tasks import payment_processor
#
# from payments_app.models import PaymentRequest
# from orders_app.models import Order
#
#
# @app.on_after_configure.connect
# def set_periodic(sender, **kwrags) -> None:
#     """
#     Функция запуска периодической задачи
#     :param sender:
#     :param kwrags:
#     """
#     sender.add_periodic_task(
#         crontab(minute="*/5"),
#         check_payments.s()
#         # fill_db.s()
#     )
#
#
# @app.task
# def check_payments() -> None:
#     """
#     Функция ежедневного добавления строки записи обменных курсов в БД.
#     """
#     # payment_processor()
#     # print('Something')
#     payment_requests = PaymentRequest.objects.all()
#     for r in payment_requests:
#         order = Order.objects.get(id=r.order)
#         if int(r.account) % 2 == 0 and r.account[-1] != '0' and len(r.account) == 8:
#             order.paid = True
#             order.braintree_id = r.account
#         else:
#             order.payment_method = 'Account number is invalid'
#         order.save()
#     payment_requests.delete()
