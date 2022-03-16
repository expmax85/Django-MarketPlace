from django.test import TestCase
from goods_app.models import Product, SpecificationsNames, Specifications, ProductCategory
from orders_app.models import Order, OrderProduct
from stores_app.models import SellerProduct, Seller
from discounts_app.models import Discount, DiscountCategory
from profiles_app.models import User


class CompareTest(TestCase):
    """ Тест сервиса сравнения товаров """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(email='test@ru.ru', password='admin732', first_name='test1',
                                        last_name='test1', phone='+7(999)999-99-99')
        cls.category = ProductCategory.objects.create(name="test_category")
        cls.seller = Seller.objects.create(name="test_seller", owner=cls.user)
        cls.discount_cat = DiscountCategory.objects.create(name="test_d_category")
        cls.discount = Discount.objects.create(name="test_discount", category=cls.discount_cat)
        for num in range(1, 3):
            SpecificationsNames.objects.create(name=f'spec{num}')
        for num in range(1, 3):
            Specifications.objects.create(value='num',
                                          current_specification=SpecificationsNames.objects.get(id=num))
        for num in range(1, 5):
            product = Product.objects.create(name=f'name{num}', category=cls.category, rating=1)
            if num < 3:
                product.specifications.add(Specifications.objects.all()[0])
            else:
                product.specifications.add(Specifications.objects.all()[1])
        for num in range(1, 5):
            SellerProduct.objects.create(seller=cls.seller,
                                         product=Product.objects.get(id=num),
                                         discount=cls.discount,
                                         price=100,
                                         price_after_discount=90,
                                         quantity=10)

    # def test_comparison_page(self):
    #     response = self.client.get('/orders/compare/')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertContains(response, Product.objects.get(id=4).name)
    #     self.assertContains(response, 'spec2')
    #     self.assertContains(response, 'no data')
    #     self.assertContains(response, '100')
    #     self.assertContains(response, '90')

    def test_cart_page(self):
        response = self.client.get('/orders/cart/')
        self.assertEquals(response.status_code, 200)

    def test_cart_template(self):
        response = self.client.get('/orders/cart/')
        self.assertTemplateUsed(response, 'orders_app/cart.html')

    def test_order_step_one(self):
        response = self.client.get('/orders/step1/')
        self.assertEquals(response.status_code, 200)

    def test_order_step_one_template(self):
        response = self.client.get('/orders/step1/')
        self.assertTemplateUsed(response, 'orders_app/order_step_one.html')

    def test_order_step_two(self):
        user = User.objects.get(email='test@ru.ru')
        self.client.force_login(user=user)
        order = Order.objects.create(customer=user)
        seller_product = SellerProduct.objects.first()
        OrderProduct.objects.create(order=order,
                                    seller_product=seller_product,
                                    final_price=100.00,
                                    quantity=5)
        response = self.client.post('/orders/step2/', {'city': 'Some city'})
        self.assertEquals(response.status_code, 200)

    def test_order_step_two_template(self):
        user = User.objects.get(email='test@ru.ru')
        self.client.force_login(user=user)
        order = Order.objects.create(customer=user)
        seller_product = SellerProduct.objects.first()
        OrderProduct.objects.create(order=order,
                                    seller_product=seller_product,
                                    final_price=100.00,
                                    quantity=5)
        response = self.client.post('/orders/step2/', {'city': 'Some city'})
        self.assertTemplateUsed(response, 'orders_app/order_step_two.html')

    def test_order_step_three(self):
        response = self.client.get('/orders/step3/')
        self.assertEquals(response.status_code, 200)

    def test_order_step_three_template(self):
        response = self.client.get('/orders/step1/')
        self.assertTemplateUsed(response, 'orders_app/order_step_one.html')
