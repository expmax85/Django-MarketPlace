from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stores_app.models import Seller
from .forms import RegisterForm


User = get_user_model()


class ProfilesAppTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='test@user.com', password='testp@sw0rd', first_name='user',
                                            last_name='test', phone='+7(922)222-22-22')

    def test_template_register_page(self):
        """Проверка шаблона регистрации"""
        response = self.client.get(reverse('profiles-polls:register'))
        self.assertTrue(response.status_code, 200)

    def test_register_form(self):
        """Проверка невозможности регистрации с идентичным email"""
        form_params = {'email': 'test@user.com',
                       'first_name': 'John',
                       'last_name': 'Doe',
                       'password1': 'testpassword',
                       'password2': 'testpassword',
                       'phone': '+7(999)993-99-99'
                       }
        form = RegisterForm(form_params)
        self.assertFalse(form.is_valid())

    def test_success_register(self):
        """Проверка успешности регистрации, при верно введенных данных"""
        response = self.client.post(
            reverse('profiles-polls:register'),
            data={
                "email": "john@example.com",
                "password1": "johndoe12",
                "password2": "johndoe12",
                "phone": "7(999)999-99-99"
            }
        )
        self.assertEqual(response.status_code, 302)
        users = User.objects.all()
        self.assertEqual(users.count(), 2)

    def test_unsuccess_register(self):
        """Проверка неуспешности регистрации, при неверно введенных данных"""
        response = self.client.post(
            reverse('profiles-polls:register'),
            data={
                "email": "john@example.com",
                "password1": "johndoe12",
                "password2": "johndoe",
                "phone": "+7(999)999-88-77"
            }
        )
        self.assertEqual(response.status_code, 200)
        users = User.objects.all()
        self.assertNotEqual(users.count(), 2)

    def test_login_user(self):
        """Проверка работы аутентификации"""
        response = self.client.post(reverse('profiles-polls:login'), {'email': self.user.email,
                                                                      'password': self.user.password})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(self.user.is_authenticated)

    def test_access_to_account_info(self):
        """Доступ к странице профиля зарегистрированным и анонимным пользователям"""
        response = self.client.get(reverse('profiles-polls:account-edit'), follow=False)
        self.assertNotEqual(response.status_code, 200)
        self.client.login(username=self.user, password='testp@sw0rd')
        response = self.client.get(reverse('profiles-polls:account-edit'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_edit_account_info_logout(self):
        """Доступ к изменению профиля анонимным пользователем"""
        response = self.client.post(reverse('profiles-polls:account-edit'), data={'city': 'testcity'}, follow=False)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(self.user.city, 'testcity')

    def test_restore_password_url_exist(self):
        """Доступ к странице восстановления пароля"""
        response = self.client.get(reverse('profiles-polls:restore-password'))
        self.assertEqual(response.status_code, 200)

    def test_restore_password_template(self):
        """Проверка шаблона восстановления пароля"""
        response = self.client.get(reverse('profiles-polls:restore-password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_reset.html')

    def test_post_restore_password(self):
        """Отпрака письма с новым паролем"""
        response = self.client.post(reverse('profiles-polls:restore-password'), {'email': self.user.email})
        self.assertEqual(response.status_code, 200)
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertIn(self.user.email, outbox[0].to)

    def test_password_was_changed(self):
        """Проверка изменения пароля"""
        old_password = self.user.password
        response = self.client.post(reverse('profiles-polls:restore-password'), {'email': self.user.email})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertNotEqual(old_password, self.user.password)

    def test_reset_phone_format(self):
        """ Проверка сброса формата телефона при сохранении пользователя """
        self.client.post(
            reverse('profiles-polls:register'),
            data={
                "email": "john@example.com",
                "password1": "johndoe12",
                "password2": "johndoe12",
                "phone": "+7(999)999-99-99"
            }
        )
        user = User.objects.get(email="john@example.com")
        self.assertTrue(user.phone == '9999999999')
