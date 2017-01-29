from django.conf.urls import url
from .views import (
    details
    )



urlpatterns = [
#    url(r'^$', list, name = 'list'),
    url(r'^(?P<name>\w+)/$', details, name = 'details'),
]