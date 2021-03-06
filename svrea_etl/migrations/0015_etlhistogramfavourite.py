# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-04 17:14
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_etl', '0014_auto_20170804_0850'),
    ]

    operations = [
        migrations.CreateModel(
            name='EtlHistogramFavourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creationdate', models.DateTimeField(blank=True, null=True)),
                ('lastupdatedate', models.DateTimeField(blank=True, null=True)),
                ('favouritename', models.CharField(blank=True, max_length=256, null=True)),
                ('comment', models.CharField(blank=True, max_length=2000, null=True)),
                ('flag', models.IntegerField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=256, null=True)),
                ('usergroup', models.CharField(blank=True, max_length=256, null=True)),
                ('histdict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
    ]
