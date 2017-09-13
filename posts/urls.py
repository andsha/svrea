from django.conf.urls import url

from .views import posts, newpost


urlpatterns =[
    url(r'^$', posts, name = 'posts'),
    url(r'new$', newpost, name = 'new'),
]