# Generated by Django 3.2.5 on 2021-08-17 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': ('Игредиент',), 'verbose_name_plural': 'Игредиенты'},
        ),
    ]
