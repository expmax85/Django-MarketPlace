from django.test import TestCase
from django.shortcuts import reverse
from goods_app.models import Product, SpecificationsNames, Specifications, ProductCategory
from stores_app.models import SellerProduct, Seller
from discounts_app.models import ProductDiscount, GroupDiscount, CartDiscount
from profiles_app.models import User
from orders_app.models import Order, OrderProduct


class PaymentTest(TestCase):
    """ Тесты оплаты заказа """
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

        self.category_1 = ProductCategory.objects.create(name="test_category_1", slug="test_category_1")
        self.category_2 = ProductCategory.objects.create(name="test_category_2", slug="test_category_2")

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
                product = Product.objects.create(name=f'name{num}', slug=f'name{num}',
                                                 category=self.category_1, rating=1)
            else:
                product = Product.objects.create(name=f'name{num}', slug=f'name{num}',
                                                 category=self.category_2, rating=1)

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

    def test_pay_with_correct_account(self):
        """Тест оплаты правильным счетом"""
        self.client.force_login(user=self.customer)
        order = Order.objects.create(customer=self.customer)

        for index in range(1, 6):
            OrderProduct.objects.create(order=order,
                                        seller_product=SellerProduct.objects.get(id=index),
                                        final_price=index * 100,
                                        quantity=1)
        order.in_order = True
        order.save()
        response = self.client.get(f'/orders/payment/account/{order.id}')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_app/payment_account.html')
        self.assertContains(response, 'Total:')
        self.assertContains(response, '1500.00$')

        response = self.client.post(reverse('orders-polls:payment_with_account', args=[order.id]),
                                    {'numero1': 45621236})
        self.assertEquals(response.status_code, 200)

    def test_pay_with_invalid_account(self):
        """Тест оплаты невалидным счетом"""
        self.client.force_login(user=self.customer)
        order = Order.objects.create(customer=self.customer)

        for index in range(1, 6):
            OrderProduct.objects.create(order=order,
                                        seller_product=SellerProduct.objects.get(id=index),
                                        final_price=index * 100,
                                        quantity=1)
        order.in_order = True
        order.save()
        response = self.client.get(f'/orders/payment/account/{order.id}')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_app/payment_account.html')
        self.assertContains(response, 'Total:')
        self.assertContains(response, '1500.00$')

        response = self.client.post(reverse('orders-polls:payment_with_account', args=[order.id]),
                                    {'numero1': 45621230})
        self.assertEquals(response.status_code, 200)
