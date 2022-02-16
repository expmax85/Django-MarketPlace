#Запуск автоматических миграций и загрузок фикстур
```
python manage.py loadscript
```
У скрипта есть аргумент и префикс. Указав аругмент with_clear, перед мирациями будут удалены старые миграции с сохранением базы данных:
```
python manage.py loadscript with_clear
```
А указав еще и префикс --db, будет удалена также и база данных:
```
python manage.py loadscript with_clear --db
```
Справка по команде:
```
python manage.py help loadscript
```

#Пароли по тестовым пользователям
 - admin@example.com: 123456
 - user@test.com: qawsed12