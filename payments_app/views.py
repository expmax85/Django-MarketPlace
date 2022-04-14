from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from payments_app.services import check_status, process_payment


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'command': openapi.Schema(type=openapi.TYPE_STRING, description='status or pay'),
        'order': openapi.Schema(type=openapi.TYPE_STRING, description='integer'),
        'account': openapi.Schema(type=openapi.TYPE_STRING, description='8-digit integer'),
    }
))
@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def payment_view(request):
    """
    Представление статуса оплаты заказа

    ::Страница: Оплата заказа
    """
    if request.method == 'POST':
        print(request.data)
        command = request.data.get('command')

        if command == 'status':
            order = request.data.get('order')
            result = check_status(order)
            return JsonResponse({'status': result})

        elif command == 'pay':
            order = request.data.get('order')
            account = request.data.get('account')
            if process_payment(order, account):
                return JsonResponse({'status': 'Payment has been put in queue'})
            return JsonResponse({'status': 'Error. Payment will not be processed'})

        else:
            return JsonResponse({'status': f'No command {command}'})
