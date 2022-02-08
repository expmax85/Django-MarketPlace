# Порядок миграций и команд для установки тестовых данных приложения profiles_app

```
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/profiles_app_groups.json
python manage.py loaddata fixtures/profiles_app_users.json
python manage.py new_site_name
python manage.py loaddata fixtures/profiles_app_social.json
```

#Пароли по тестовым пользователям
 - admin@example.com: 123456
 - user@test.com: qawsed12