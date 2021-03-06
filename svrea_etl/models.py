from django.db import models
from django.contrib.postgres.fields import JSONField


class EtlHistory(models.Model):
    historydate = models.DateTimeField(null=True, blank=True)
    etldate = models.DateTimeField(null=True, blank=True)
    etlperiod = models.CharField(max_length=10, null = True, blank=True)
    stage   = models.CharField(max_length = 50, null=True, blank=True)
    status  = models.CharField(max_length = 50, null=True, blank=True)
    details = models.CharField(max_length = 500, null=True, blank=True)


class EtlListingsDaily(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True) 
    property_type           = models.CharField(max_length=20, null=True, blank=True)
    active_listings         = models.IntegerField(null=True, blank=True)
    sold_today              = models.IntegerField(null=True, blank=True)
    listing_price_avg       = models.IntegerField(null=True, blank=True)
    listing_price_med       = models.IntegerField(null=True, blank=True)
    listing_price_sqm_avg   = models.IntegerField(null=True, blank=True)
    listing_price_sqm_med   = models.IntegerField(null=True, blank=True)
    listing_area_avg        = models.IntegerField(null=True, blank=True)
    listing_area_med        = models.IntegerField(null=True, blank=True)
    listing_rent_avg        = models.IntegerField(null=True, blank=True)
    listing_rent_med        = models.IntegerField(null=True, blank=True)
    sold_price_avg          = models.IntegerField(null=True, blank=True)
    sold_price_med          = models.IntegerField(null=True, blank=True)
    sold_price_sqm_avg      = models.IntegerField(null=True, blank=True)
    sold_price_sqm_med      = models.IntegerField(null=True, blank=True)
    sold_area_avg           = models.IntegerField(null=True, blank=True)
    sold_area_med           = models.IntegerField(null=True, blank=True)
    sold_rent_avg           = models.IntegerField(null=True, blank=True)
    sold_rent_med           = models.IntegerField(null=True, blank=True)
    sold_daysbeforesold_avg = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1)
    sold_propertyage_avg = models.FloatField(null=True, blank=True)

    class Meta:
        index_together = ['record_firstdate', 'geographic_name']

    


class EtlListingsWeekly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    weekofyear              = models.IntegerField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
    property_type = models.CharField(max_length=20, null=True, blank=True)
    active_listings         = models.IntegerField(null=True, blank=True)
    sold_today              = models.IntegerField(null=True, blank=True)
    listing_price_avg       = models.IntegerField(null=True, blank=True)
    listing_price_med       = models.IntegerField(null=True, blank=True)
    listing_price_sqm_avg   = models.IntegerField(null=True, blank=True)
    listing_price_sqm_med   = models.IntegerField(null=True, blank=True)
    listing_area_avg        = models.IntegerField(null=True, blank=True)
    listing_area_med        = models.IntegerField(null=True, blank=True)
    listing_rent_avg        = models.IntegerField(null=True, blank=True)
    listing_rent_med        = models.IntegerField(null=True, blank=True)
    sold_price_avg          = models.IntegerField(null=True, blank=True)
    sold_price_med          = models.IntegerField(null=True, blank=True)
    sold_price_sqm_avg      = models.IntegerField(null=True, blank=True)
    sold_price_sqm_med      = models.IntegerField(null=True, blank=True)
    sold_area_avg           = models.IntegerField(null=True, blank=True)
    sold_area_med           = models.IntegerField(null=True, blank=True)
    sold_rent_avg           = models.IntegerField(null=True, blank=True)
    sold_rent_med           = models.IntegerField(null=True, blank=True)
    sold_daysbeforesold_avg = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1)
    sold_propertyage_avg = models.FloatField(null=True, blank=True)

    class Meta:
        index_together = ['record_firstdate', 'geographic_name']


class EtlListingsMonthly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    monthofyear              = models.IntegerField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
    property_type = models.CharField(max_length=20, null=True, blank=True)
    active_listings         = models.IntegerField(null=True, blank=True)
    sold_today              = models.IntegerField(null=True, blank=True)
    listing_price_avg       = models.IntegerField(null=True, blank=True)
    listing_price_med       = models.IntegerField(null=True, blank=True)
    listing_price_sqm_avg   = models.IntegerField(null=True, blank=True)
    listing_price_sqm_med   = models.IntegerField(null=True, blank=True)
    listing_area_avg        = models.IntegerField(null=True, blank=True)
    listing_area_med        = models.IntegerField(null=True, blank=True)
    listing_rent_avg        = models.IntegerField(null=True, blank=True)
    listing_rent_med        = models.IntegerField(null=True, blank=True)
    sold_price_avg          = models.IntegerField(null=True, blank=True)
    sold_price_med          = models.IntegerField(null=True, blank=True)
    sold_price_sqm_avg      = models.IntegerField(null=True, blank=True)
    sold_price_sqm_med      = models.IntegerField(null=True, blank=True)
    sold_area_avg           = models.IntegerField(null=True, blank=True)
    sold_area_med           = models.IntegerField(null=True, blank=True)
    sold_rent_avg           = models.IntegerField(null=True, blank=True)
    sold_rent_med           = models.IntegerField(null=True, blank=True)
    sold_daysbeforesold_avg = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1)
    sold_propertyage_avg = models.FloatField(null=True, blank=True)

    class Meta:
        index_together = ['record_firstdate', 'geographic_name']


class EtlListingsQuarterly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    quarterofyear              = models.IntegerField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
    property_type = models.CharField(max_length=20, null=True, blank=True)
    active_listings         = models.IntegerField(null=True, blank=True)
    sold_today              = models.IntegerField(null=True, blank=True)
    listing_price_avg       = models.IntegerField(null=True, blank=True)
    listing_price_med       = models.IntegerField(null=True, blank=True)
    listing_price_sqm_avg   = models.IntegerField(null=True, blank=True)
    listing_price_sqm_med   = models.IntegerField(null=True, blank=True)
    listing_area_avg        = models.IntegerField(null=True, blank=True)
    listing_area_med        = models.IntegerField(null=True, blank=True)
    listing_rent_avg        = models.IntegerField(null=True, blank=True)
    listing_rent_med        = models.IntegerField(null=True, blank=True)
    sold_price_avg          = models.IntegerField(null=True, blank=True)
    sold_price_med          = models.IntegerField(null=True, blank=True)
    sold_price_sqm_avg      = models.IntegerField(null=True, blank=True)
    sold_price_sqm_med      = models.IntegerField(null=True, blank=True)
    sold_area_avg           = models.IntegerField(null=True, blank=True)
    sold_area_med           = models.IntegerField(null=True, blank=True)
    sold_rent_avg           = models.IntegerField(null=True, blank=True)
    sold_rent_med           = models.IntegerField(null=True, blank=True)
    sold_daysbeforesold_avg = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1)
    sold_propertyage_avg = models.FloatField(null=True, blank=True)

    class Meta:
        index_together = ['record_firstdate', 'geographic_name']


class EtlListingsYearly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
    property_type = models.CharField(max_length=20, null=True, blank=True)
    active_listings         = models.IntegerField(null=True, blank=True)
    sold_today              = models.IntegerField(null=True, blank=True)
    listing_price_avg       = models.IntegerField(null=True, blank=True)
    listing_price_med       = models.IntegerField(null=True, blank=True)
    listing_price_sqm_avg   = models.IntegerField(null=True, blank=True)
    listing_price_sqm_med   = models.IntegerField(null=True, blank=True)
    listing_area_avg        = models.IntegerField(null=True, blank=True)
    listing_area_med        = models.IntegerField(null=True, blank=True)
    listing_rent_avg        = models.IntegerField(null=True, blank=True)
    listing_rent_med        = models.IntegerField(null=True, blank=True)
    sold_price_avg          = models.IntegerField(null=True, blank=True)
    sold_price_med          = models.IntegerField(null=True, blank=True)
    sold_price_sqm_avg      = models.IntegerField(null=True, blank=True)
    sold_price_sqm_med      = models.IntegerField(null=True, blank=True)
    sold_area_avg           = models.IntegerField(null=True, blank=True)
    sold_area_med           = models.IntegerField(null=True, blank=True)
    sold_rent_avg           = models.IntegerField(null=True, blank=True)
    sold_rent_med           = models.IntegerField(null=True, blank=True)
    sold_daysbeforesold_avg = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1)
    sold_propertyage_avg = models.FloatField(null=True, blank=True)

    class Meta:
        index_together = ['record_firstdate', 'geographic_name']


class EtlTimeSeriesFavourite(models.Model):
    creationdate = models.DateTimeField(null=True, blank=True)
    lastupdatedate = models.DateTimeField(null=True, blank=True)
    favouritename = models.CharField(max_length=256, null=True, blank=True)
    comment = models.CharField(max_length=2000, null=True, blank=True)
    flag = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=256, null=True, blank=True)
    usergroup = models.CharField(max_length=256, null=True, blank=True)
    timeseriesdict = JSONField(null=True, blank=True)

class EtlHistogramFavourite(models.Model):
    creationdate = models.DateTimeField(null=True, blank=True)
    lastupdatedate = models.DateTimeField(null=True, blank=True)
    favouritename = models.CharField(max_length=256, null=True, blank=True)
    comment = models.CharField(max_length=2000, null=True, blank=True)
    flag = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=256, null=True, blank=True)
    usergroup = models.CharField(max_length=256, null=True, blank=True)
    histdict = JSONField(null=True, blank=True)