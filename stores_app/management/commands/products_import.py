import json
from json import JSONDecodeError
import logging
import time
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from goods_app.models import Product
from discounts_app.models import ProductDiscount
from stores_app.models import Seller, SellerProduct, ProductImportFile, ImportOrder


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
fh = logging.FileHandler('import_log.txt', encoding='utf-8')
fh.setFormatter(formatter)
logger.addHandler(fh)


class Command(BaseCommand):
    """ Реализует импорт товаров у продавца из json """

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    @classmethod
    def update_product(cls, product: SellerProduct, price: int, quantity: int) -> SellerProduct:
        """ Обновляет товар, если он уже есть у продавца """

        product.price = price
        product.quantity += quantity
        product.save()
        return product

    @classmethod
    def create_discount(cls, discount: dict[str, any], seller: Seller, product: SellerProduct) -> None:
        """ Создает скидку на товар """

        discount = ProductDiscount.objects.get_or_create(seller=seller,
                                                         set_discount=True,
                                                         percent=discount['percent'],
                                                         amount=discount['amount'],
                                                         name=discount['title'],
                                                         description=discount['description'],
                                                         valid_from=discount['valid_from'],
                                                         valid_to=discount['valid_to'],
                                                         is_active=True)

        product.product_discounts.add(discount[0])

    @classmethod
    def save_log_info(cls, user: str, start_time: datetime, file_id: int) -> None:
        """ Сохраняет часть лога в модель файла импорта """

        with open('import_log.txt', 'r') as imp_log:
            result = imp_log.read()
            file_log = result[result.find(f'{user} starts import at {start_time}>'):result.find(
                f'{user} finished importing which started in {start_time}')]
            curr_file = ProductImportFile.objects.get(id=file_id)
            curr_file.log_info = file_log
            curr_file.errors = file_log.count('Error:')
            curr_file.warnings = file_log.count('Warning:')
            curr_file.status = 'Complete'
            curr_file.save()

    @classmethod
    def semaphore(cls, value: bool) -> None:
        """ Переключает флаг очереди в базе данных """

        flag = ImportOrder.objects.all()[0]
        if value:
            flag.can_import = True
            flag.save()
        else:
            flag.can_import = False
            flag.save()

    def handle(self, *args, **options) -> None:
        """ Парсит файл импорта """

        self.semaphore(False)
        time.sleep(20)
        start_time = datetime.now()
        logger.info(f'{args[1]} starts import at {start_time}>')
        with open(f'uploads/import/products/{args[0]}', 'r') as json_file:
            try:
                data = json.loads(json_file.read())
                logger.info('the file has been read>')
            except JSONDecodeError:
                logger.info('Error: bad json structure>')
        for item_name, features in data.items():
            try:
                product = Product.objects.get(name=item_name)
                logger.info(f'product "{product.name}" was found>')
                try:
                    seller = Seller.objects.get(name=features['store'])
                    logger.info(f'seller "{seller.name}" was found>')
                except (ObjectDoesNotExist, KeyError):
                    logger.info(f'Error: your store {features["store"]} does not exist>')
                    continue
                try:
                    new_product = self.update_product(SellerProduct.objects.get(seller=seller, product=product),
                                                      features['price'],
                                                      features['quantity'])
                    logger.info('your product was updated>')
                except ObjectDoesNotExist:
                    new_product = SellerProduct.objects.create(seller=seller,
                                                               product=product,
                                                               price=features['price'],
                                                               quantity=features['quantity'],
                                                               )
                    logger.info('your product was created>')
                except KeyError:
                    logger.info('Error: no price or quantity>')
                try:
                    self.create_discount(features['discount'], seller, new_product)
                    logger.info('your discount was created>')
                except KeyError:
                    logger.info('Warning: no discount in import file or bad discount structure>')
                new_product.save()
                logger.info(f'"{item_name}" imported>')
            except ObjectDoesNotExist:
                logger.info(f'Error: "{item_name}" was not found in marketplace>')
                continue
        logger.info(f'{args[1]} finished importing which started in {start_time}>')
        self.save_log_info(args[1], start_time, args[2])
        self.semaphore(True)


