# Generated by Django 3.1.2 on 2020-10-27 03:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('icon', models.CharField(max_length=100, null=True)),
                ('order', models.IntegerField()),
                ('state', models.CharField(default='B', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Permissionmenu',
            fields=[
                ('permission', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='auth.permission')),
                ('order', models.IntegerField()),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acl.menu')),
            ],
        ),
        migrations.CreateModel(
            name='Modules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('app_name', models.CharField(blank=True, max_length=200, null=True)),
                ('route', models.CharField(blank=True, max_length=250, null=True)),
                ('order', models.IntegerField()),
                ('parent', models.CharField(blank=True, max_length=15, null=True)),
                ('state', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModuleGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acl.modules')),
            ],
        ),
    ]
