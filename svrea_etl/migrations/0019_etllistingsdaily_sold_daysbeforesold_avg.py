# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-14 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_etl', '0018_remove_etllistingsdaily_sold_daysbeforesold_avg'),
    ]

    operations = [
        migrations.AddField(
            model_name='etllistingsdaily',
            name='sold_daysbeforesold_avg',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True),
        ),
    ]
