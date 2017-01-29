from django.db import models


class Info(models.Model):
    date_started = models.DateTimeField(auto_now=True, primary_key=True)
    script = models.CharField(max_length = 200)
    status = models.CharField(max_length=200)
    comment = models.CharField(max_length=500)

    class Meta:
        permissions = (("can_run_script", "Can run script"), ("can_see_history", "Can See History"), )
