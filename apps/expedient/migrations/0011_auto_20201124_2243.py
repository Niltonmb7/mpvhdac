# Generated by Django 3.1.2 on 2020-11-24 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expedient', '0010_auto_20201123_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='date_update',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='expedient',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='expedient',
            name='date_update',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]