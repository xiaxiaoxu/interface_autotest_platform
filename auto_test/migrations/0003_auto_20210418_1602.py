# Generated by Django 2.2.4 on 2021-04-18 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto_test', '0002_auto_20210405_2026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testcase',
            name='assert_key',
        ),
        migrations.AlterField(
            model_name='testcase',
            name='maintainer',
            field=models.CharField(max_length=1024, verbose_name='编写人员'),
        ),
    ]