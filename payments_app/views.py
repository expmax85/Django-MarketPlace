from django.http import JsonResponse
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from payments_app.services import check_status, process_payment


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def payment_view(request):
    if request.method == 'POST':
        command = request.POST.get('command')

        if command == 'status':
            order = request.POST.get('order')
            result = check_status(order)
            return JsonResponse({'status': result})

        elif command == 'pay':
            order = request.POST.get('order')
            account = request.POST.get('account')
            if process_payment(order, account):
                return JsonResponse({'status': 'Payment processed'})
            return JsonResponse({'status': 'Payment not processed'})

        else:
            return JsonResponse({'status': f'No command {command}'})
