# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-09 17:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_script', '0003_address_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='dateinactive',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]