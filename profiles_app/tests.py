from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm


User = get_user_model()


class RestoredPasswordTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='test@user.com', password='testp@sw0rd', first_name='user',
                                            last_name='test', phone='+79222222222')

    def test_register_form(self):
        """Проверка невозможности регистрации с идентичным email"""
        form_params = {'email': 'test@user.com',
                       'first_name': 'John',
                       'last_name': 'Doe',
                       'password1': 'testpassword',
                       'password2': 'testpassword',
                       'phone': '9999939999'
                       }
        form = RegisterForm(form_params)
        self.assertFalse(form.is_valid())

    def test_success_register(self):
        """Проверка успешности регистрации, при верно введенных данных"""
        response = self.client.post(
            reverse("register"),
            data={
                "email": "john@example.com",
                "password1": "johndoe12",
                "password2": "johndoe12",
                "phone": "+9999999999"
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 2)

    def test_unsuccess_register(self):
        """Проверка неуспешности регистрации, при неверно введенных данных"""
        response = self.client.post(
            reverse("register"),
            data={
                "email": "john@example.com",
                "password1": "johndoe12",
                "password2": "johndoe12",
                "phone": "sadasd"
            }
        )
        self.assertEqual(response.status_code, 200)
        users = get_user_model().objects.all()
        self.assertNotEqual(users.count(), 2)

    def test_login_user(self):
        """Проверка работы аутентификации"""
        response = self.client.post('/users/login/', {'email': self.user.email,
                                                'password': self.user.password})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(self.user.is_authenticated)

    def test_restore_password_url_exist(self):
        """Доступ к странице восстановления пароля"""
        response = self.client.get('/users/restore_password/')
        self.assertEqual(response.status_code, 200)

    def test_restore_password_template(self):
        """Проверка шаблона восстановления пароля"""
        response = self.client.get(reverse('restore_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles_app/restore_password.html')

    def test_post_restore_password(self):
        """Отпрака письма с новым паролем"""
        response = self.client.post(reverse('restore_password'), {'email': self.user.email})
        self.assertEqual(response.status_code, 200)
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertIn(self.user.email, outbox[0].to)

    def test_password_was_changed(self):
        """Проверка изменения пароля"""
        old_password = self.user.password
        response = self.client.post(reverse('restore_password'), {'email': self.user.email})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertNotEqual(old_password, self.user.password)
