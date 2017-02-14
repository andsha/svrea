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
    datepublished       = models.DateTimeField(db_index=True, default=None)
    sourceid            = models.ForeignKey('Source', on_delete=models.CASCADE)
    addressid           = models.ForeignKey('Address', on_delete=models.CASCADE)
    latitude            = models.DecimalField(max_digits=10, decimal_places=8, default=None)
    longitude           = models.DecimalField(max_digits=10, decimal_places=8, default=None)
    constructionyear    = models.IntegerField(default=None)
    rent                = models.IntegerField(default=None)
    url                 = models.CharField(max_length=250, default=None)
    rooms               = models.CharField(max_length=10, default=None)
    propertytype        = models.CharField(max_length=50, default=None)
    plotarea            = models.DecimalField(max_digits=5, decimal_places=1, default=None)
    additionalarea      = models.DecimalField(max_digits=5, decimal_places=1, default=None)
    livingarea          = models.DecimalField(max_digits=5, decimal_places=1, default=None)
    floor               = models.CharField(max_length=10, default=None)
    isnewconstruction   = models.BooleanField(default=None)
    datesold            = models.DateTimeField(default=None)
    isactive            = models.BooleanField(db_index=True, default=None)
    dateinactive        = models.DateTimeField(default=None)
    latestprice         = models.IntegerField(default=None)


class Source(models.Model):
    sourceid            = models.AutoField(primary_key=True)
    name                = models.CharField(max_length=250)
    sourcetype          = models.CharField(max_length=50)
    url                 = models.CharField(max_length=250)


class Address(models.Model):
    addressid           = models.AutoField(primary_key=True)
    house               = models.CharField(max_length=10)
    street              = models.CharField(max_length=250)
    city                = models.CharField(max_length=50)
    municipality        = models.CharField(max_length=50)
    county              = models.CharField(max_length=50)
    areaname            = models.CharField(max_length=50)

    class Meta:
        index_together = ['street', 'city', 'municipality', 'county' ]


class Pricehistory(models.Model):
    booliid             = models.ForeignKey('Listings', on_delete=models.CASCADE)
    price               = models.IntegerField()
    date                = models.DateTimeField()
    ifsoldprice         = models.BooleanField()


