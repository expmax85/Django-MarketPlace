import os

from django.core import management
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'delete old migrations and database'

    def add_arguments(self, parser):
        parser.add_argument('with_clear', type=str, help='Delete only migrations files')

        # Optional argument
        parser.add_argument('--db', action='store_true', help='Prefix for del db', )

    def handle(self, *args, **kwargs):
        if kwargs['with_clear']:
            self._remove_old_migrations()
            self._remove_database()
        elif kwargs['prefix']:
            self._remove_old_migrations()
        management.call_command('makemigrations')
        management.call_command('migrate')
        management.call_command('new_site_name')
        folder_fixture = 'fixtures/'
        fixtures_list = self._get_list_fixtures()
        err_list = []
        n_iteration = len(fixtures_list) * 2
        self.stdout.write(f'\nFIXTURES LOAD...')
        while fixtures_list:
            err_list = []
            for item in fixtures_list:
                try:
                    self.stdout.write(f'Loading {item}')
                    management.call_command('loaddata', ''.join([folder_fixture, item]))
                    fixtures_list.remove(item)
                except IntegrityError:
                    self.stdout.write(f'IntegrityError when loading {item}')
                    if item not in err_list:
                        err_list.append(item)
            if n_iteration == 0:
                break
            n_iteration -= 1

        if err_list:
            self.stdout.write(f'Not all fixtures was loading. Check it:')
            print([item for item in err_list])
        else:
            self.stdout.write(f'\nAll commands and loading was successfully!')

    def _get_list_fixtures(self):
        path = os.path.abspath('fixtures')
        return os.listdir(path=path)

    def _remove_old_migrations(self):
        list_dirs = ['banners_app', 'discounts_app', 'goods_app', 'orders_app', 'profiles_app', 'stores_app']
        for item in list_dirs:
            path = ''.join([os.path.abspath(item), '\migrations'])
            for file in os.listdir(path):
                if not file.startswith('__'):
                    os.remove(os.path.join(path, file))

    def _remove_database(self):
        os.remove(os.path.abspath('db.sqlite3'))
