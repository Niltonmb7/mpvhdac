# Generated by Django 3.1.2 on 2020-11-11 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expedient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('state', models.CharField(choices=[('A', 'Activo'), ('I', 'Inactivo')], max_length=1)),
            ],
            options={
                'db_table': '"mpv"."type_document"',
            },
        ),
    ]
