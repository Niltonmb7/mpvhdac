# Generated by Django 3.1.2 on 2020-12-15 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acl', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='modules',
            name='url_external',
            field=models.URLField(blank=True, max_length=250, null=True),
        ),
    ]