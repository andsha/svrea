from django.db import models


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


class EtlListingsWeekly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    weekofyear              = models.IntegerField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
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


class EtlListingsMonthly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    monthofyear              = models.IntegerField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
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


class EtlListingsQuaterly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    quaterofyear              = models.IntegerField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
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


class EtlListingsYearly(models.Model):
    record_firstdate        = models.DateTimeField(null=True, blank=True)
    geographic_type         = models.CharField(max_length = 50, null=True, blank=True)
    geographic_name         = models.CharField(max_length = 50, null=True, blank=True)
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