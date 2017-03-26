# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-26 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EtlHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('historydate', models.DateTimeField(blank=True, null=True)),
                ('stage', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('details', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EtlListings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_date', models.DateTimeField(blank=True, null=True)),
                ('geographic_type', models.CharField(blank=True, max_length=50, null=True)),
                ('geographic_name', models.CharField(blank=True, max_length=50, null=True)),
                ('active_listings', models.IntegerField(blank=True, null=True)),
                ('sold_today', models.IntegerField(blank=True, null=True)),
                ('listing_price_avg', models.IntegerField(blank=True, null=True)),
                ('listing_price_85', models.IntegerField(blank=True, null=True)),
                ('listing_price_15', models.IntegerField(blank=True, null=True)),
                ('listing_price_med', models.IntegerField(blank=True, null=True)),
                ('listing_price_sqm_avg', models.IntegerField(blank=True, null=True)),
                ('listing_price_sqm_med', models.IntegerField(blank=True, null=True)),
                ('listing_price_sqm_85', models.IntegerField(blank=True, null=True)),
                ('listing_price_sqm_15', models.IntegerField(blank=True, null=True)),
                ('listing_area_avg', models.IntegerField(blank=True, null=True)),
                ('listing_area_max', models.IntegerField(blank=True, null=True)),
                ('listing_area_min', models.IntegerField(blank=True, null=True)),
                ('listing_area_med', models.IntegerField(blank=True, null=True)),
                ('listing_rent_avg', models.IntegerField(blank=True, null=True)),
                ('listing_rent_max', models.IntegerField(blank=True, null=True)),
                ('listing_rent_min', models.IntegerField(blank=True, null=True)),
                ('listing_rent_med', models.IntegerField(blank=True, null=True)),
                ('sold_price_avg', models.IntegerField(blank=True, null=True)),
                ('sold_price_med', models.IntegerField(blank=True, null=True)),
                ('sold_price_85', models.IntegerField(blank=True, null=True)),
                ('sold_price_15', models.IntegerField(blank=True, null=True)),
                ('sold_price_sqm_avg', models.IntegerField(blank=True, null=True)),
                ('sold_price_sqm_med', models.IntegerField(blank=True, null=True)),
                ('sold_price_sqm_85', models.IntegerField(blank=True, null=True)),
                ('sold_price_sqm_15', models.IntegerField(blank=True, null=True)),
                ('sold_area_avg', models.IntegerField(blank=True, null=True)),
                ('sold_area_max', models.IntegerField(blank=True, null=True)),
                ('sold_area_min', models.IntegerField(blank=True, null=True)),
                ('sold_area_med', models.IntegerField(blank=True, null=True)),
                ('sold_rent_avg', models.IntegerField(blank=True, null=True)),
                ('sold_rent_max', models.IntegerField(blank=True, null=True)),
                ('sold_rent_min', models.IntegerField(blank=True, null=True)),
                ('sold_rent_med', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
