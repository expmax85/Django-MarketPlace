from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from stores_app.models import Seller

User = get_user_model()


class StoresTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='test@user.com', password='testp@sw0rd', first_name='user',
                                            last_name='test', phone='9222222222')
        ct = ContentType.objects.create(app_label='profiles_app', model='User')
        perm = Permission.objects.create(content_type=ct, codename='Sellers', name='can_sell')
        cls.user.user_permissions.add(perm)
        cls.store = Seller.objects.create(name='test_store', slug='test_store_1', owner=cls.user)

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

    def test_add_new_store_without_perm(self):
        testuser = User.objects.create(email='test2@user.com', password='testp@sw0rd2', first_name='user2',
                                       last_name='test2', phone='9333333333')
        self.client.login(email=testuser.email, password='testp@sw0rd2')
        response = self.client.get(reverse('stores-polls:add-store'), follow=False)
        self.assertNotEqual(response.status_code, 200)
