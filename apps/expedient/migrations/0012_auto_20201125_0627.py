# Generated by Django 3.1.2 on 2020-11-25 06:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('expedient', '0011_auto_20201124_2243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expedient',
            name='id',
        ),
        migrations.AddField(
            model_name='expedient',
            name='epedient_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=150, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
