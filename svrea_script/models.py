from django.db import models


class Info(models.Model):
    started = models.DateTimeField(auto_now=True)
    user_name = models.CharField(max_length=50, default='None')
    config = models.CharField(max_length = 200)
    status = models.CharField(max_length=200)
    comment = models.CharField(max_length=500)

    class Meta:
        permissions = (("can_run_script", "Can run script"), ("can_see_history", "Can See History"), )
