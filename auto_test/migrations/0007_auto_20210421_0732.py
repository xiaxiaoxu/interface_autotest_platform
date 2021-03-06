# Generated by Django 2.2.4 on 2021-04-21 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto_test', '0006_auto_20210421_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('env', models.CharField(default='', max_length=50, verbose_name='环境')),
                ('ip', models.CharField(default='', max_length=50, verbose_name='ip')),
                ('port', models.CharField(default='', max_length=100, verbose_name='端口')),
                ('remark', models.CharField(max_length=100, null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '模块信息表',
                'verbose_name_plural': '模块信息表',
            },
        ),
        migrations.AlterField(
            model_name='testcase',
            name='case_name',
            field=models.CharField(max_length=50, verbose_name='用例名称'),
        ),
    ]
