# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_script', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='isactive',
            field=models.NullBooleanField(),
        ),
    ]
