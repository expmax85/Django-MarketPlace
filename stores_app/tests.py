import random
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory
from django.urls import reverse

from goods_app.models import Product, ProductCategory
from stores_app.forms import AddStoreForm, AddSellerProductForm
from stores_app.models import Seller, SellerProduct
from stores_app.services import StoreServiceMixin

User = get_user_model()


class StoresTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='test@user.com', password='testp@sw0rd', first_name='user',
                                            last_name='test', phone='9222222222')
        ct = ContentType.objects.create(app_label='profiles_app', model='User')
        perm = Permission.objects.create(content_type=ct, codename='Sellers', name='can_sell')
        cls.user.user_permissions.add(perm)
        group = Group.objects.create(name='Sellers')
        group.user_set.add(cls.user)
        Seller.objects.bulk_create([Seller(name='test_store', slug='test_store_1', owner=cls.user),
                                   Seller(name='test_store_2', slug='test_store_2', owner=cls.user)])
        categories = [
            ProductCategory.objects.create(name="test_category_1", slug="test_category_1"),
            ProductCategory.objects.create(name="test_category_2", slug="test_category_2")
        ]
        Product.objects.bulk_create([Product(name=f'name{num}', slug=f'name{num}', category=random.choice(categories), rating=1)
                                     for num in range(1, 4)])
        seller = Seller.objects.all().last()
        SellerProduct.objects.bulk_create([SellerProduct(seller=seller,
                                                         product=Product.objects.get(id=num),
                                                         price=num * 100,
                                                         quantity=100)
                                           for num in range(1, 4)])

    def test_no_get_seller_room(self):
        """ Доступ к личному кабинету продавцов без прав"""

        testuser = User.objects.create(email='test2@user.com', password='testp@sw0rd2', first_name='user2',
                                       last_name='test2', phone='9333333333')
        self.client.login(email=testuser.email, password='testp@sw0rd2')
        response = self.client.get(reverse('stores-polls:sellers-room'), follow=False)
        self.assertNotEqual(response.status_code, 200)

    def test_get_seller_room(self):
        """ Доступ к личному кабинету продавцов c правами"""

        self.client.login(email=self.user.email, password='testp@sw0rd')
        response = self.client.get(reverse('stores-polls:sellers-room'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_add_new_store(self):
        """ Создание нового магазина продавцом """
        self.temp_image = tempfile.NamedTemporaryFile(suffix='.jpg').name
        response = self.client.get(reverse('stores-polls:add-store'), follow=False)
        self.assertNotEqual(response.status_code, 200)

        self.client.login(email=self.user.email, password='testp@sw0rd')
        response = self.client.get(reverse('stores-polls:add-store'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_delete_store(self):
        """ Удаление магазина продавцом """
        response = self.client.get(reverse('stores-polls:delete-store'), follow=False)
        self.assertNotEqual(response.status_code, 200)

        factory = RequestFactory()
        request = factory.get(reverse('stores-polls:delete-store'), {'id': 'test_store_2'})
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        pre_count = Seller.objects.all().count()
        StoreServiceMixin.remove_store(request)
        post_count = Seller.objects.all().count()
        self.assertNotEqual(pre_count, post_count)
        self.assertEqual(pre_count - post_count, 1)

    def test_add_new_sellerproduct(self):
        """ Создание нового продукта продавца """
        response = self.client.get(reverse('stores-polls:add-store-product'), follow=False)
        self.assertNotEqual(response.status_code, 200)

        self.client.login(email=self.user.email, password='testp@sw0rd')
        response = self.client.get(reverse('stores-polls:add-store-product'), follow=False)
        self.assertEqual(response.status_code, 200)

        pre_count = SellerProduct.objects.all().count()
        self.assertEqual(pre_count, 3)
        product = Product.objects.get(id=2)
        seller = Seller.objects.all().first()
        form = AddSellerProductForm({'seller': seller, 'product': product, 'price': 444, 'quantity': 4})
        form.save(commit=False)
        StoreServiceMixin.create_seller_product(data=form.cleaned_data)
        post_count = SellerProduct.objects.all().count()
        self.assertNotEqual(post_count, pre_count)
        self.assertEqual(post_count - pre_count, 1)

    def test_delete_sellerproduct(self):
        """ Удаление магазина продавцом """
        response = self.client.get(reverse('stores-polls:delete-seller-product'), follow=False)
        self.assertNotEqual(response.status_code, 200)

        factory = RequestFactory()
        request = factory.get(reverse('stores-polls:delete-seller-product'), {'id': '1'})
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        pre_count = SellerProduct.objects.all().count()
        StoreServiceMixin.remove_seller_product(request)
        post_count = SellerProduct.objects.all().count()
        self.assertNotEqual(pre_count, post_count)
        self.assertEqual(pre_count - post_count, 1)
