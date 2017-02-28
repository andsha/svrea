from django.db import models
from django.contrib.postgres.fields import JSONField


class Info(models.Model):
    started = models.DateTimeField(auto_now=True)
    user_name = models.CharField(max_length=50, default='None')
    config = models.CharField(max_length = 200)
    status = models.CharField(max_length=200)
    comment = models.CharField(max_length=500, default='None')

    class Meta:
        permissions = (("can_run_script", "Can run script"), ("can_see_history", "Can See History"), )

class Log(models.Model):
    when = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=20)
    entry = models.CharField(max_length=500, default="None")


class Rawdata(models.Model):
    downloaded          = models.DateTimeField(auto_now=True)
    uploaded            = models.BooleanField(default=False)
    type                = models.CharField(max_length = 50)
    areacode            = models.IntegerField()
    rawdata             = JSONField()


class Aux(models.Model):
    changed             = models.DateTimeField(auto_now=True)
    key                 = models.CharField(max_length=200)
    value               = models.CharField(max_length=200)


class Listings(models.Model):
    booliid             = models.IntegerField(primary_key=True)
    datepublished       = models.DateTimeField(db_index=True, null=True, blank=True)
    source              = models.ForeignKey('Source', on_delete=models.CASCADE, null=True, blank=True)
    address             = models.ForeignKey('Address', on_delete=models.CASCADE, null=True, blank=True)
    latitude            = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude           = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    constructionyear    = models.IntegerField(null=True, blank=True)
    rent                = models.IntegerField(null=True, blank=True)
    url                 = models.CharField(max_length=250, null=True, blank=True)
    rooms               = models.CharField(max_length=10, null=True, blank=True)
    propertytype        = models.CharField(max_length=50, null=True, blank=True)
    plotarea            = models.IntegerField(null=True, blank=True)
    additionalarea      = models.IntegerField(null=True, blank=True)
    livingarea          = models.IntegerField(null=True, blank=True)
    floor               = models.CharField(max_length=10, null=True, blank=True)
    isnewconstruction   = models.NullBooleanField(null=True, blank=True)
    datesold            = models.DateTimeField(null=True, blank=True)
    isactive            = models.NullBooleanField(db_index=True, null=True, blank=True)
    dateinactive        = models.DateTimeField(null=True, blank=True)
    latestprice         = models.IntegerField(null=True, blank=True)


class Source(models.Model):
    sourceid            = models.AutoField(primary_key=True)
    name                = models.CharField(max_length=250, null=True, blank=True)
    sourcetype          = models.CharField(max_length=50, null=True, blank=True)
    url                 = models.CharField(max_length=250, null=True, blank=True)


class Address(models.Model):
    addressid           = models.AutoField(primary_key=True)
    house               = models.CharField(max_length=10, null=True, blank=True)
    street              = models.CharField(max_length=250, null=True, blank=True)
    city                = models.CharField(max_length=50, null=True, blank=True)
    municipality        = models.CharField(max_length=50, null=True, blank=True)
    county              = models.CharField(max_length=50, null=True, blank=True)
    areaname            = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        index_together = ['street', 'city', 'municipality', 'county' ]


class Pricehistory(models.Model):
    booliid             = models.ForeignKey('Listings', on_delete=models.CASCADE)
    price               = models.IntegerField(null=True, blank=True)
    date                = models.DateTimeField(null=True, blank=True)
    issoldprice         = models.BooleanField(null=True, blank=True)


