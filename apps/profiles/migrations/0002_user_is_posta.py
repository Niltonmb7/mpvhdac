# Generated by Django 3.1.2 on 2020-12-20 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_posta',
            field=models.BooleanField(default=False),
        ),
    ]