# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-14 10:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('police', '0004_user_profile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='civilian',
            name='job',
            field=models.TextField(default='None'),
        ),
        migrations.AlterField(
            model_name='civilian',
            name='salary',
            field=models.IntegerField(default=0),
        ),
    ]