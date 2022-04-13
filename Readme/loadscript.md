#Запуск автоматических миграций и загрузок фикстур
```
python manage.py loadscript no_clear
```
При этом будут загружены фикстуры, находящиеся в папке fixtures, либо в папке, уцказанной в параметре FOLDER_FIXTURES файла настроек settings.py

У скрипта также есть аргумент и префикс. Указав вместо no_clear аругмент with_clear, перед мирациями будут удалены старые миграции с сохранением базы данных:
```
python manage.py loadscript with_clear
```
А указав еще и префикс --db, будет удалена также и база данных(только для БД .sqlite):
```
python manage.py loadscript with_clear --db
```
Справка по команде:
```
python manage.py help loadscript
```