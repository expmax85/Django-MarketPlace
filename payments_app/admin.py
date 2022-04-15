from django.contrib import admin
from payments_app.models import PaymentRequest


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'account']
