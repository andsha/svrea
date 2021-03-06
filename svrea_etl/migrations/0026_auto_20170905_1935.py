# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-05 19:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('svrea_etl', '0025_auto_20170822_1827'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='etllistingsdaily',
            index_together=set([('record_firstdate', 'geographic_name')]),
        ),
        migrations.AlterIndexTogether(
            name='etllistingsmonthly',
            index_together=set([('record_firstdate', 'geographic_name')]),
        ),
        migrations.AlterIndexTogether(
            name='etllistingsquarterly',
            index_together=set([('record_firstdate', 'geographic_name')]),
        ),
        migrations.AlterIndexTogether(
            name='etllistingsweekly',
            index_together=set([('record_firstdate', 'geographic_name')]),
        ),
        migrations.AlterIndexTogether(
            name='etllistingsyearly',
            index_together=set([('record_firstdate', 'geographic_name')]),
        ),
    ]
