from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs) -> None:
        site_model = apps.get_model('sites', 'Site')
        site = site_model.objects.get(id=1)
        site.domain = 'http://127.0.0.1:8000'
        site.name = 'http://127.0.0.1:8000'
        site.save()
        self.stdout.write(self.style.SUCCESS(
            'Domain and site name was successfully changed!'
        ))
