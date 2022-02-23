from django.test import TestCase
from goods_app.models import Product, SpecificationsNames, Specifications, ProductCategory
from stores_app.models import SellerProduct, Seller
from discounts_app.models import Discount, DiscountCategory
from profiles_app.models import User


class CompareTest(TestCase):
    """ Тест сервиса сравнения товаров, будет изменен после разработки сервиса добавления в список сравнения """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email='test@ru.ru', password='admin732', first_name='test1',
                                        last_name='test1', phone='+7(999)999-99-99')
        category = ProductCategory.objects.create(name="test_category")
        seller = Seller.objects.create(name="test_seller", owner=user)
        discount_cat = DiscountCategory.objects.create(name="test_d_category")
        discount = Discount.objects.create(name="test_discount", category=discount_cat)
        for num in range(1, 3):
            SpecificationsNames.objects.create(name=f'spec{num}')
        for num in range(1, 3):
            Specifications.objects.create(value='num',
                                          current_specification=SpecificationsNames.objects.get(id=num))
        for num in range(1, 5):
            product = Product.objects.create(name=f'name{num}', category=category, rating=1)
            if num < 3:
                product.specifications.add(Specifications.objects.all()[0])
            else:
                product.specifications.add(Specifications.objects.all()[1])
        for num in range(1, 5):
            SellerProduct.objects.create(seller=seller,
                                         product=Product.objects.get(id=num),
                                         discount=discount,
                                         price=100,
                                         price_after_discount=90,
                                         quantity=10)

    def test_comparison_page(self):
        response = self.client.get('/orders/compare/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, Product.objects.get(id=4).name)
        self.assertContains(response, 'spec2')
        self.assertContains(response, 'no data')
        self.assertContains(response, '100')
        self.assertContains(response, '90')




