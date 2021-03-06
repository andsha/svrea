import datetime

from django.core.urlresolvers import reverse
from django.db import models



class Posts (models.Model):
    dateofcreation = models.DateTimeField(null=True, blank=True)
    createdby = models.CharField(null=True, blank=True, max_length=256)
    title = models.CharField(null=True,blank=True,max_length=1000)
    text = models.TextField(null=True, blank=True)

    class Meta:
        permissions = (("can_mke_new_posts", "Can make new posts"),
                       )

    def get_detailed_url(self):
        return reverse("posts:details", kwargs={"id": self.id})

    def get_edit_url(self):
        return reverse("posts:edit", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("posts:delete", kwargs={"id": self.id})