import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(['payments_app', 'orders_app'], related_name='tasks', force=True)
