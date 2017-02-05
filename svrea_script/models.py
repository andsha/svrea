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
    downloaded = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length = 50)
    areacode = models.IntegerField()
    rawdata = JSONField()