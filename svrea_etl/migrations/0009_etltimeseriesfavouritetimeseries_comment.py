# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-31 17:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_etl', '0008_etltimeseriesfavouritetimeseries'),
    ]

    operations = [
        migrations.AddField(
            model_name='etltimeseriesfavouritetimeseries',
            name='comment',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
