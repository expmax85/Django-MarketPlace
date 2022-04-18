from config.celery import app
from django.core.management import call_command
from stores_app.models import ImportOrder


@app.task(bind=True)
def start_import(self, task_vars):
    if ImportOrder.objects.get(id=1).can_import:
        call_command('products_import', task_vars[0], task_vars[1], task_vars[2])
    else:
        self.retry(countdown=40)
