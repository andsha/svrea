# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-26 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_etl', '0006_auto_20170724_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='etlhistory',
            name='etlperiod',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
