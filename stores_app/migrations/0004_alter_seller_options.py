# Generated by Django 4.0.1 on 2022-02-08 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores_app', '0003_alter_seller_options_alter_seller_address_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seller',
            options={'verbose_name': 'store', 'verbose_name_plural': 'stores'},
        ),
    ]
