# Generated by Django 3.1.2 on 2020-10-08 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_property_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='author',
            new_name='author_id',
        ),
    ]
