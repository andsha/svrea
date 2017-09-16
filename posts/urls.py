from django.conf.urls import url

from .views import posts, newpost, details, edit, delete


urlpatterns =[
    url(r'^$', posts, name = 'posts'),
    url(r'new$', newpost, name = 'new'),
    url(r'^edit/(?P<id>\d+)/$', edit, name='edit'),
    url(r'^delete/(?P<id>\d+)/$', delete, name='delete'),
    url(r'^(?P<id>\d+)/$', details, name='details'),
]