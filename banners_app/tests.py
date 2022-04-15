from django.test import TestCase
from discounts_app.models import ProductDiscount
from banners_app.models import Banner
from banners_app.services import banner
from datetime import datetime, timedelta
from profiles_app.models import User
from goods_app.models import ProductCategory, Product
from stores_app.models import Seller, SellerProduct


class BannersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email='test@user.com', password='testp@sw0rd', first_name='user',
                                        last_name='test', phone='+7(922)222-22-22')

        seller = Seller.objects.create(name='Test Store', slug='test-store', owner=user)
        category = ProductCategory.objects.create(name='Test category', slug='test-category')

        for index in range(10):
            product = Product.objects.create(category=category, name=f'Product №{index}',
                                             slug=f'Product №{index}', is_published=True)
            seller_product = SellerProduct(seller=seller, product=product, price=100.00, quantity=100)
            seller_product.save()

        for index in range(6):
            valid_from = datetime.strftime(datetime.today() - timedelta(days=3 - index), '%Y-%m-%d %H:%M:%S')
            valid_to = datetime.strftime(datetime.today() - timedelta(days=1 - index, hours=-1), '%Y-%m-%d %H:%M:%S')
            discount = ProductDiscount.objects.create(
                seller=seller,
                name=f'Discount {index}',
                slug=f'discount-{index}',
                description=f'Description {index}',
                percent=50,
                valid_from=valid_from,
                valid_to=valid_to,
                is_active=True
            )

            discount.seller_products.set([SellerProduct.objects.get(id=index + 1)])

            Banner.objects.create(
                discount=discount,
                title=f'Banner - {index}',
                description=f'Banner description {index}'
            )

    def test_main_page_exists(self):
        """
        Тест выдачи 3 рандомных баннеров на главной странице
        """
        response = self.client.get('/')
        banners = banner()

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Banner - 1')
        self.assertContains(response, 'Banner description 3')

        self.assertTemplateUsed(response, 'goods_app/index.html')
        self.assertEqual(len(banners), 3)
