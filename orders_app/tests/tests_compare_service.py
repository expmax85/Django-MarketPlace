from django.test import TestCase
from django.shortcuts import reverse
from goods_app.models import Product, SpecificationsNames, Specifications, ProductCategory
from orders_app.models import Order, OrderProduct, ViewedProduct
from stores_app.models import SellerProduct, Seller
from discounts_app.models import ProductDiscount
from profiles_app.models import User


class CompareTest(TestCase):
    """ Тесты сервиса сравнения товаров """

    def setUp(self):
        self.user = User.objects.create(email='test@ru.ru', password='admin732', first_name='test1',
                                        last_name='test1', phone='+7(999)999-99-99')
        self.category = ProductCategory.objects.create(name="test_category", slug="test_category")
        self.seller = Seller.objects.create(name="test_seller", slug="test_store", owner=self.user)
        self.discount = ProductDiscount.objects.create(name="test_discount", seller=self.seller)
        for num in range(1, 3):
            SpecificationsNames.objects.create(name=f'spec{num}')
        for num in range(1, 3):
            Specifications.objects.create(value='num',
                                          current_specification=SpecificationsNames.objects.get(id=num))
        for num in range(1, 5):
            product = Product.objects.create(name=f'name{num}', slug=f'name{num}', category=self.category, rating=1)
            if num < 3:
                product.specifications.add(Specifications.objects.all()[0])
            else:
                product.specifications.add(Specifications.objects.all()[1])
        for num in range(1, 5):
            seller_product = SellerProduct.objects.create(seller=self.seller,
                                                          product=Product.objects.get(id=num),
                                                          price=100,
                                                          quantity=10)
            seller_product.product_discounts.set([self.discount])

    def test_comparison_page(self):
        """ Добавляет товары в список для сравнения и проверяет страницу сравнения """

        for idx in range(1, 5):
            self.client.get(reverse('orders-polls:add-to-compare', kwargs={'product_id': idx}), HTTP_REFERER='/')
        response = self.client.get('/orders/compare/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, Product.objects.get(id=4).name)
        self.assertContains(response, 'spec2')
        self.assertContains(response, 'no data')
        self.assertContains(response, '100')
        # self.assertContains(response, '90')

    def test_compared_quantity(self):
        """ Добавляет товары в список для сравнения и проверяет отображение их кол-ва не некоторых страницах """

        for idx in range(1, 5):
            self.client.get(reverse('orders-polls:add-to-compare', kwargs={'product_id': idx}), HTTP_REFERER='/')
        response = self.client.get('/')
        self.assertContains(response, '<span class="CartBlock-amount">4</span>')
        response = self.client.get('/orders/compare/')
        self.assertContains(response, '<span class="CartBlock-amount">4</span>')
        response = self.client.get('/orders/cart/')
        self.assertContains(response, '<span class="CartBlock-amount">4</span>')


class HistoryOrderTest(TestCase):
    """ Тесты сервиса истории заказов """

    def setUp(self):
        self.user = User.objects.create(email='test@ru.ru', password='admin732', first_name='test1',
                                        last_name='test1', phone='+7(999)999-99-99')
        self.order1 = Order.objects.create(customer=self.user, delivery='reg', payment_method='card', paid='True',
                                           in_order=True)
        self.order2 = Order.objects.create(customer=self.user, delivery='express', payment_method='cash', paid='False',
                                           in_order=True)

        self.category = ProductCategory.objects.create(name="test_category", slug="test_category")
        self.seller = Seller.objects.create(name="test_seller", slug="test_store", owner=self.user)
        self.discount = ProductDiscount.objects.create(name="test_discount",
                                                       seller=self.seller)

        for num in range(1, 5):
            Product.objects.create(name=f'name{num}', slug=f'name{num}', category=self.category, rating=1)
        for num in range(1, 5):
            SellerProduct.objects.create(seller=self.seller,
                                         product=Product.objects.get(id=num),
                                         price=100,
                                         quantity=10)
        for num in range(4):
            OrderProduct.objects.create(order=self.order2, seller_product=SellerProduct.objects.all()[num],
                                        final_price=100)

    def test_history_page(self):
        """ Страница истории заказов """

        self.client._login(self.user, backend='django.contrib.auth.backends.ModelBackend')
        response = self.client.get('/orders/history/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paid')
        self.assertContains(response, 'Not paid')
        self.assertContains(response, 'Regular delivery')
        self.assertContains(response, 'Express delivery')
        self.assertContains(response, 'Card')
        self.assertContains(response, 'Random account')

    def test_order_detail_page(self):
        """ Детальная страница заказа """

        self.client._login(self.user, backend='django.contrib.auth.backends.ModelBackend')
        response = self.client.get('/orders/history/2')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Express delivery')
        self.assertContains(response, 'Not paid')
        self.assertContains(response, 'Random account')
        self.assertContains(response, 'name3')
        self.assertContains(response, 'test_seller')
        # self.assertContains(response, '400$')


class HistoryViewedTest(TestCase):
    """ Тесты сервиса истории просмотров """

    def setUp(self):
        self.user = User.objects.create(email='test@ru.ru', password='admin732', first_name='test1',
                                        last_name='test1', phone='+7(999)999-99-99')
        self.category = ProductCategory.objects.create(name="test_category")
        self.seller = Seller.objects.create(name="test_seller", owner=self.user)
        self.discount = ProductDiscount.objects.create(name="test_discount",
                                                       seller=self.seller)
        for num in range(1, 5):
            Product.objects.create(name=f'name{num}', slug=f'name{num}', category=self.category, rating=1)
        for num in range(1, 5):
            SellerProduct.objects.create(seller=self.seller,
                                         product=Product.objects.get(id=num),
                                         price=100,
                                         quantity=10)

    def test_viewed(self):
        """ Добавление в просмотренные """

        self.client._login(self.user, backend='django.contrib.auth.backends.ModelBackend')
        self.client.get('/orders/add_viewed/', data={'seller_product_id': 3})
        viewed = ViewedProduct.objects.all().values('product__product__name')
        viewed = [name['product__product__name'] for name in viewed]
        self.assertTrue('name3' in viewed)
