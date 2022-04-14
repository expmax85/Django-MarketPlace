import openpyxl

from django.contrib.admindocs.views import simplify_regex
from django.core.management.base import BaseCommand
from django.urls import URLPattern, URLResolver
from config import urls


class ViewDoesNotExist(Exception):
    pass


class RegexURLPattern:
    pass


class RegexURLResolver:
    pass


SECTION = {
    'discounts-polls': 'Скидки',
    'goods-polls': 'Каталог',
    'orders-polls': 'Заказы и Корзины',
    'account-payment': 'Заказы и Корзины',
    'profiles-polls': 'Пользователи',
    'stores-polls': 'Продавцы',
    'settings-polls': 'Админ-панель',
    'admin': 'Админ-панель',
}


class Command(BaseCommand):

    def handle(self, *args, **options):

        views = []
        view_functions = self.extract_views_from_urlpatterns(urls.urlpatterns)
        for (func, regex, url_name) in view_functions:
            url_name = url_name or ''
            url = simplify_regex(regex)
            methods = 'GET'
            try:
                for key in func.__dict__['view_class'].__dict__.keys():
                    if not key.startswith('__'):
                        if str(key) == 'post':
                            methods += ', POST'
            except KeyError:
                if func.__name__.startswith('post'):
                    methods = 'POST'
            try:
                index = func.__doc__.rfind("::Страница:")
                page = func.__doc__[index + 11:].rstrip()
                doc = func.__doc__[:index].strip()
            except (AttributeError, TypeError):
                page = ""
                doc = func.__doc__

            views.append("{url}|{url_name}|{page}|{doc}|{methods}".format(
                url_name=url_name,
                url=url,
                page=page,
                doc=doc,
                methods=methods
            ).strip())

        views = [row.split('|', 4) for row in views]
        self.import_to_excel(views)

    def extract_views_from_urlpatterns(self, urlpatterns, base='', namespace=None):
        """
        Return a list of views from a list of urlpatterns.
        Each object in the returned list is a three-tuple: (view_func, regex, name)
        """
        views = []
        for p in urlpatterns:
            if isinstance(p, (URLPattern, RegexURLPattern)):
                try:
                    if not p.name:
                        name = p.name
                    elif namespace:
                        name = '{0}:{1}'.format(namespace, p.name)
                    else:
                        name = p.name
                    pattern = str(p.pattern)
                    views.append((p.callback, base + pattern, name))
                except ViewDoesNotExist:
                    continue
            elif isinstance(p, (URLResolver, RegexURLResolver)):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                if namespace and p.namespace:
                    _namespace = '{0}:{1}'.format(namespace, p.namespace)
                else:
                    _namespace = (p.namespace or namespace)
                pattern = str(p.pattern)
                views.extend(self.extract_views_from_urlpatterns(patterns, base + pattern, namespace=_namespace))
            elif hasattr(p, 'url_patterns') or hasattr(p, '_get_url_patterns'):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                views.extend(self.extract_views_from_urlpatterns(patterns, base + str(p.pattern), namespace=namespace))
            else:
                raise TypeError("%s does not appear to be a urlpattern object" % p)
        return views

    def import_to_excel(self, data):

        book = openpyxl.Workbook()
        sheet = book.active
        sheet['A1'] = 'Раздел'
        sheet['B1'] = 'Страница'
        sheet['C1'] = 'Описание'
        sheet['D1'] = 'Методы'
        sheet['E1'] = 'URL'
        sheet['F1'] = 'Пространство имен'
        sheet['G1'] = 'Имя URL'
        sheet['H1'] = 'Комментарии'

        i = 2
        for line in data:
            if not line[0].startswith('/admin/') and \
               not line[0].startswith('/accounts/') and \
               not line[0].startswith('/i18nsetlang/') and \
               not line[0].startswith('/__debug__/') and \
               not line[0].startswith('/uploads/') and \
               not line[0].startswith('/api_auth/') and \
               not line[0].startswith('/swagger/'):

                sheet[f'E{str(i)}'] = line[0]
                sheet[f'C{str(i)}'] = line[3]
                sheet[f'B{str(i)}'] = line[2]
                sheet[f'D{str(i)}'] = line[4]
                url_name = line[1].split(':')
                try:
                    sheet[f'F{str(i)}'] = url_name[0]
                    sheet[f'G{str(i)}'] = url_name[1]
                    sheet[f'A{str(i)}'] = SECTION[str(url_name[0])]
                except (IndexError, KeyError):
                    sheet[f'G{str(i)}'] = url_name[0]
                    sheet[f'A{str(i)}'] = SECTION[str(url_name[0])]
                i += 1
        book.save('urls.xlsx')
        book.close()
