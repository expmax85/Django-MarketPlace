import os

from django.core import management
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
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
