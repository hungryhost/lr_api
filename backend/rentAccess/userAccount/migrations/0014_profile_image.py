# Generated by Django 3.1.2 on 2020-10-08 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAccount', '0013_auto_20201008_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]