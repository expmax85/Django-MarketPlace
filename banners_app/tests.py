from django.test import TestCase
from discounts_app.models import ProductDiscount
from banners_app.models import Banner
from banners_app.services import banner
from datetime import datetime, timedelta


class BannersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for index in range(6):
            valid_from = datetime.strftime(datetime.today() - timedelta(days=3 - index), '%Y-%m-%d %H:%M:%S')
            valid_to = datetime.strftime(datetime.today() - timedelta(days=1 - index, hours=-1), '%Y-%m-%d %H:%M:%S')
            discount = ProductDiscount.objects.create(
                name=f'Discount {index}',
                description=f'Description {index}',
                valid_from=valid_from,
                valid_to=valid_to
            )

            Banner.objects.create(
                discount=discount,
                title=f'Banner - {index}',
                description=f'Banner description {index}'
            )

    def test_main_page_exists(self):
        """
        Тест выдачи 3 рандомных баннеров на главной странице
        """
        response = self.client.get('')
        banners = banner()

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Banner - 1')
        self.assertContains(response, 'Banner description 3')

        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(len(banners), 3)
