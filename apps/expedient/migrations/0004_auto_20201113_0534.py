# Generated by Django 3.1.2 on 2020-11-13 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expedient', '0003_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expedient',
            name='date_register',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
