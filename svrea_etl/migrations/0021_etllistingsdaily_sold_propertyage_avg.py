# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-17 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_etl', '0020_auto_20170814_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='etllistingsdaily',
            name='sold_propertyage_avg',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
