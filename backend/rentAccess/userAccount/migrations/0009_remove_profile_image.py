# Generated by Django 3.1.2 on 2020-10-08 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userAccount', '0008_auto_20201008_1618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
    ]