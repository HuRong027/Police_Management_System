# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-15 06:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('police', '0005_auto_20160414_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='police',
            name='post',
            field=models.CharField(default='Inspector', max_length=30),
        ),
        migrations.AlterField(
            model_name='police',
            name='rank',
            field=models.IntegerField(default=5),
        ),
    ]