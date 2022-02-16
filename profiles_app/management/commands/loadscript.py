import os

from django.core import management
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from config.settings import INSTALLED_APPS, DATABASES


class Command(BaseCommand):
    help = 'Run all migrations and load fixtures'

    def add_arguments(self, parser):
        parser.add_argument('with_clear', type=str, help='Delete only migrations files')
        # Optional argument
        parser.add_argument('--db', action='store_true', help='Prefix for deleting database', )

    def handle(self, *args, **kwargs):
        if kwargs['with_clear']:
            self._remove_old_migrations()
        if kwargs['db']:
            self._remove_database()
        management.call_command('makemigrations')
        management.call_command('migrate')
        management.call_command('new_site_name')
        folder_fixture = 'fixtures/'
        fixtures_list = self._get_list_fixtures()
        err_list = []
        n_iteration = len(fixtures_list) * 2
        self.stdout.write(f'\nFIXTURES LOAD...')
        while fixtures_list:
            err_list.clear()
            for item in fixtures_list:
                try:
                    self.stdout.write(f'Loading {item}')
                    management.call_command('loaddata', ''.join([folder_fixture, item]))
                    fixtures_list.remove(item)
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(f'IntegrityError when loading {item}'))
                    if item not in err_list:
                        err_list.append(item)
            if n_iteration == 0:
                break
            n_iteration -= 1
        if err_list:
            self.stdout.write(self.style.WARNING(f'Not all fixtures was loading. Check it:'))
            self.stdout.write(self.style.WARNING(err_list))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nAll commands and loadings was successfully!'))

    def _remove_old_migrations(self):
        list_apps = self._get_apps_list()
        for item in list_apps:
            path = ''.join([os.path.abspath(item), '\migrations'])
            for file in os.listdir(path):
                if not file.startswith('__'):
                    os.remove(os.path.join(path, file))

    def _remove_database(self):
        path_db = DATABASES['default']['NAME']
        os.remove(path_db)

    def _get_list_fixtures(self):
        path = os.path.abspath('fixtures')
        return os.listdir(path=path)

    def _get_apps_list(self):
        list_apps = []
        for item in INSTALLED_APPS:
            path = ''.join([os.path.abspath(item), '\migrations'])
            if os.path.exists(path):
                list_apps.append(item)
        return list_apps
