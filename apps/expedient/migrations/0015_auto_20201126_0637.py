# Generated by Django 3.1.2 on 2020-11-26 06:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expedient', '0014_expedient_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expedient',
            old_name='epedient_id',
            new_name='expedient_id',
        ),
    ]
