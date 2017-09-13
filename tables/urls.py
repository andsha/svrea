from django.conf.urls import url

from .views import index, summary


urlpatterns =[
    url(r'^$', index, name = 'summary'),
    url(r'summary$', summary, name = 'summary'),
]