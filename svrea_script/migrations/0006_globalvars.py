# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-08 13:09
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_script', '0005_auto_20170808_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalVars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('var', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('charval', models.CharField(blank=True, max_length=256, null=True)),
                ('dicval', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
    ]
