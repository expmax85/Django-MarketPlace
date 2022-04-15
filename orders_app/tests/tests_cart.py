from django.test import TestCase
from django.shortcuts import reverse
from goods_app.models import Product, SpecificationsNames, Specifications, ProductCategory
from stores_app.models import SellerProduct, Seller
from discounts_app.models import ProductDiscount, GroupDiscount, CartDiscount
from profiles_app.models import User


class CartTest(TestCase):
    """ Тесты работы корзины """

    def setUp(self):
        self.user = User.objects.create(email='test@ru.ru',
                                        password='admin732',
                                        first_name='user1',
                                        last_name='lastname1',
                                        phone='+7(999)999-99-99')

        self.customer = User.objects.create(email='customer@ru.ru',
                                            password='customer732',
                                            first_name='user2',
                                            last_name='lastname2',
                                            phone='+7(999)999-88-88')

        self.category_1 = ProductCategory.objects.create(name="test_category_1",
                                                         slug="test_category_1")

        self.category_2 = ProductCategory.objects.create(name="test_category_2",
                                                         slug="test_category_2")

        self.seller_1 = Seller.objects.create(name="test_seller_1",
                                              slug="test_seller_1",
                                              owner=self.user)

        self.seller_2 = Seller.objects.create(name="test_seller_2",
                                              slug="test_seller_2",
                                              owner=self.user)

        self.product_discount_1 = ProductDiscount.objects.create(name="test_product_discount_1",
                                                                 slug="test_product_discount_1",
                                                                 description="test_product_discount_description_1",
                                                                 type_of_discount='p',
                                                                 priority=2,
                                                                 percent=15,
                                                                 is_active=True,
                                                                 seller=self.seller_1)

        self.product_discount_2 = ProductDiscount.objects.create(name="test_product_discount_2",
                                                                 slug="test_product_discount_2",
                                                                 description="test_product_discount_description_2",
                                                                 type_of_discount='f',
                                                                 priority=3,
                                                                 amount=200,
                                                                 is_active=True,
                                                                 set_discount=True,
                                                                 seller=self.seller_1)

        self.category_discount = GroupDiscount.objects.create(name="test_category_discount",
                                                              slug="test_product_discount",
                                                              description="test_category_discount_description_2",
                                                              type_of_discount='p',
                                                              priority=2,
                                                              percent=10,
                                                              is_active=True,
                                                              seller=self.seller_1,
                                                              product_category=self.category_1)

        self.cart_discount = CartDiscount.objects.create(name="test_cart_discount",
                                                         slug="test_cart_discount",
                                                         description="test_cart_discount_description",
                                                         type_of_discount='p',
                                                         priority=1,
                                                         percent=5,
                                                         is_active=True,
                                                         seller=self.seller_1,
                                                         min_quantity_threshold=3,
                                                         max_quantity_threshold=10)

        for num in range(1, 3):
            SpecificationsNames.objects.create(name=f'spec{num}')

        for num in range(1, 3):
            Specifications.objects.create(value='num',
                                          current_specification=SpecificationsNames.objects.get(id=num))

        for num in range(1, 6):
            if num < 3:
                product = Product.objects.create(name=f'name{num}', slug=f'name{num}', category=self.category_1, rating=1)
            else:
                product = Product.objects.create(name=f'name{num}', slug=f'name{num}', category=self.category_2, rating=1)

            if num < 3:
                product.specifications.add(Specifications.objects.all()[0])
            else:
                product.specifications.add(Specifications.objects.all()[1])

        for num in range(1, 6):
            SellerProduct.objects.create(seller=self.seller_1,
                                         product=Product.objects.get(id=num),
                                         price=num * 100,
                                         quantity=100)

        for num in range(1, 6):
            SellerProduct.objects.create(seller=self.seller_2,
                                         product=Product.objects.get(id=num),
                                         price=num * 150,
                                         quantity=100)

        SellerProduct.objects.get(id=1).product_discounts.set([self.product_discount_1,
                                                               self.product_discount_2])

        SellerProduct.objects.get(id=4).product_discounts.set([self.product_discount_2])

    def test_cart_page(self):
        """Тест статуса ответа и шаблона страницы корзины"""
        response = self.client.get('/orders/cart/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_app/cart.html')

    def test_cart_empty_contents(self):
        """Тест проверки содержания пустой корзины"""
        response = self.client.get('/orders/cart/')
        self.assertTemplateUsed(response, 'orders_app/cart.html')
        self.assertContains(response, 'No products yet')
        self.assertContains(response, '0$')

    def test_cart_add_product_for_anonym_user(self):
        """Тест добавления товара в корзину анонимным пользователем"""
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 2}), HTTP_REFERER='/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name2')
        self.assertContains(response, '200')
        self.assertContains(response, '180')

    def test_cart_add_product_for_logged_user(self):
        """Тест добавления товара в корзину аутентифицированным пользователем"""
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 3}), HTTP_REFERER='/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name3')
        self.assertContains(response, '300')

    def test_cart_add_3_products_for_anonym_user(self):
        """Тест добавления 3 товаров в корзину анонимным пользователем"""
        for index in range(3, 6):
            self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/')
        response = self.client.get(reverse('orders:cart_detail'))

        self.assertContains(response, 'name3')
        self.assertContains(response, 'name4')
        self.assertContains(response, 'name5')

        self.assertContains(response, '300')
        self.assertContains(response, '400')
        self.assertContains(response, '500')

        self.assertContains(response, '285')
        self.assertContains(response, '380')
        self.assertContains(response, '475')

        self.assertContains(response, '1140')

    def test_cart_add_3_products_for_logged_user(self):
        """Тест добавления 3 товаров в корзину аутентифицированным пользователем"""
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        for index in range(3, 6):
            self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/')
        response = self.client.get(reverse('orders:cart_detail'))

        self.assertContains(response, 'name3')
        self.assertContains(response, 'name4')
        self.assertContains(response, 'name5')

        self.assertContains(response, '300')
        self.assertContains(response, '400')
        self.assertContains(response, '500')

        self.assertContains(response, '285')
        self.assertContains(response, '380')
        self.assertContains(response, '475')

        self.assertContains(response, '1140')

    def test_cart_remove_product_for_anonym_user(self):
        """Тест удаления из корзины одного из товаров анонимным пользователем"""
        for index in range(3, 6):
            self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/')
        self.client.get(reverse('orders:cart_remove', kwargs={'product_id': 3}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders:cart_detail'))

        self.assertNotContains(response, 'name3')
        self.assertContains(response, 'name4')
        self.assertContains(response, 'name5')

        self.assertNotContains(response, '300')
        self.assertContains(response, '400')
        self.assertContains(response, '500')

    def test_cart_remove_product_for_logged_user(self):
        """Тест удаления из корзины одного из товаров аутентифицированным пользователем"""
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        for index in range(3, 6):
            self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/')
        self.client.get(reverse('orders:cart_remove', kwargs={'product_id': 3}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders:cart_detail'))

        self.assertNotContains(response, 'name3')
        self.assertContains(response, 'name4')
        self.assertContains(response, 'name5')

        self.assertNotContains(response, '300')
        self.assertContains(response, '400')
        self.assertContains(response, '500')

    def test_cart_add_3_products_and_one_more_added_for_anonym_user(self):
        """
        Тест добавления в корзину уже имеющегося товара анонимным пользователем
        Меняется колчество этого товара и общая сумма корзины
        """
        for index in range(3, 6):
            self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/')
        self.client.get(reverse('orders-polls:cart_add', kwargs={'product_id': 3}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))

        self.assertContains(response, 'name3')
        self.assertContains(response, 'name4')
        self.assertContains(response, 'name5')

        self.assertContains(response, '300')
        self.assertContains(response, '2')
        self.assertContains(response, '400')
        self.assertContains(response, '500')

        self.assertContains(response, '285')
        self.assertContains(response, '380')
        self.assertContains(response, '475')

        self.assertContains(response, '1500')
        self.assertContains(response, '1425')

    def test_cart_add_3_products_and_one_more_added_for_logged_user(self):
        """
        Тест добавления в корзину уже имеющегося товара аутентифицированным пользователем
        Меняется колчество этого товара и общая сумма корзины
        """
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        for index in range(3, 6):
            self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/')
        self.client.get(reverse('orders-polls:cart_add', kwargs={'product_id': 3}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))

        self.assertContains(response, 'name3')
        self.assertContains(response, 'name4')
        self.assertContains(response, 'name5')

        self.assertContains(response, '300')
        self.assertContains(response, '2')
        self.assertContains(response, '400')
        self.assertContains(response, '500')

        self.assertContains(response, '285')
        self.assertContains(response, '380')
        self.assertContains(response, '475')

        self.assertContains(response, '1500')
        self.assertContains(response, '1425')

    def test_cart_add_1_and_2_products_and_change_discounts_for_anonym_user(self):
        """
        Тест изменения скидок на товар при добавлении ещё одного товара из набора анонимным пользователем
        Меняется цена со скидкой на первый товар
        """
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 1}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')
        self.assertContains(response, '100')
        self.assertContains(response, '90')

        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 4}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))

        self.assertContains(response, 'name1')
        self.assertContains(response, 'name4')

        self.assertContains(response, '100')
        self.assertContains(response, '60')
        self.assertContains(response, '400')
        self.assertContains(response, '240')
        self.assertContains(response, '500')
        self.assertContains(response, '300')

    def test_cart_add_1_and_2_products_and_change_discounts_for_logged_user(self):
        """
        Тест изменения скидок на товар при добавлении ещё одного товара из набора аутентифицированным пользователем
        Меняется цена со скидкой на первый товар
        """
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 1}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')
        self.assertContains(response, '100')
        self.assertContains(response, '90')

        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 4}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))

        self.assertContains(response, 'name1')
        self.assertContains(response, 'name4')

        self.assertContains(response, '100')
        self.assertContains(response, '60')
        self.assertContains(response, '400')
        self.assertContains(response, '240')
        self.assertContains(response, '500')
        self.assertContains(response, '300')

    def test_cart_change_quantity_for_anonym_user(self):
        """Тест изменения количества товара селектом из корзины анонимным пользователем"""
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 1}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')
        self.assertContains(response, '1')
        self.client.post('/orders/cart/1', {'option': 1, 'amount': 9},
                         HTTP_REFERER='/orders/cart/')

        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')
        self.assertContains(response, '9')
        self.assertContains(response, '900')

    def test_cart_change_quantity_for_logged_user(self):
        """Тест изменения количества товара селектом из корзины аутентифицированным пользователем"""
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 1}), HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')
        self.assertContains(response, '1')
        self.client.post('/orders/cart/1', {'option': 1, 'amount': 9},
                         HTTP_REFERER='/orders/cart/')

        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')
        self.assertContains(response, '9')
        self.assertContains(response, '900')

    def test_cart_change_store_in_product_select_for_anonym_user(self):
        """Тест выбора другого магазина для товара в корзине для анонимного пользователя"""
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 1}), HTTP_REFERER='/orders/cart/')
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 6}), HTTP_REFERER='/orders/cart/')

        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')

        self.assertContains(response, '1')

        self.assertContains(response, '100')
        self.assertContains(response, '150')
        self.assertContains(response, '250')

        self.client.post('/orders/cart/1', {'amount': 2, 'option': 6}, HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')

        self.assertContains(response, '3')

        self.assertContains(response, '150')
        self.assertContains(response, '450')

    def test_cart_change_store_in_product_select_for_logged_user(self):
        """Тест выбора другого магазина для товара в корзине для аутентифицированного пользователя"""
        self.client._login(self.customer, backend='django.contrib.auth.backends.ModelBackend')
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 1}), HTTP_REFERER='/orders/cart/')
        self.client.get(reverse('orders:cart_add', kwargs={'product_id': 6}), HTTP_REFERER='/orders/cart/')

        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')

        self.assertContains(response, '1')

        self.assertContains(response, '100')
        self.assertContains(response, '150')
        self.assertContains(response, '250')

        self.client.post('/orders/cart/1', {'amount': 2, 'option': 6}, HTTP_REFERER='/orders/cart/')
        response = self.client.get(reverse('orders-polls:cart_detail'))
        self.assertContains(response, 'name1')

        self.assertContains(response, '3')

        self.assertContains(response, '150')
        self.assertContains(response, '450')

    # def test_cart_merge_after_login(self):
    #     """Тест слияния корзин после аутентификации пользователя"""
    #     self.client.login(username='customer@ru.ru', password='customer732')
    #
    #     for index in range(1, 4):
    #         self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/orders/cart/')
    #
    #     response = self.client.get(reverse('orders-polls:cart_detail'))
    #     self.assertContains(response, 'name1')
    #     self.assertContains(response, 'name2')
    #     self.assertContains(response, 'name3')
    #
    #     self.assertContains(response, '600')
    #
    #     self.client.logout()
    #
    #     for index in range(3, 6):
    #         self.client.get(reverse('orders:cart_add', kwargs={'product_id': index}), HTTP_REFERER='/orders/cart/')
    #
    #     response = self.client.get(reverse('orders-polls:cart_detail'))
    #
    #     self.assertNotContains(response, 'name1')
    #     self.assertNotContains(response, 'name2')
    #
    #     self.assertContains(response, 'name3')
    #     self.assertContains(response, 'name4')
    #     self.assertContains(response, 'name5')
    #
    #     self.assertContains(response, '1200')
    #
    #     self.client.post(reverse('profiles-polls:login'), {'email': 'customer@ru.ru',
    #                                                        'password': 'customer732'})
    #
    #     response = self.client.get(reverse('orders-polls:cart_detail'))
    #
    #     self.assertTrue(self.user.is_authenticated)
    #     self.assertContains(response, 'name1')
    #     self.assertContains(response, 'name2')
    #     self.assertContains(response, 'name3')
    #     self.assertContains(response, 'name4')
    #     self.assertContains(response, 'name5')
    #
    #     self.assertContains(response, '1500')
