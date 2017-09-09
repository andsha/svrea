import datetime

from django.db import models


class Posts (models.Model):
    dateofcreation = models.DateTimeField(null=True, blank=True)
    createdby = models.CharField(null=True, blank=True, max_length=256)
    source = models.CharField(null=True, blank=True, max_length=1000)
    text = models.TextField(null=True, blank=True)


