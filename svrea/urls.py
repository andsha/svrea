"""svrea URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from .views import (
    index,
    maps,
    #maps_sold,
    plots_histograms
)

from svrea_script.views import script_info as svrea_script_info
from svrea_script.views import script_data as svrea_script_data
from svrea_script.views import script_run as svrea_script_run
from svrea_script.views import script_logs as svrea_script_logs

from uauth.views import uregister

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name = 'index'),
    url(r'^register/', uregister, name = 'register'),
    url(r'^users/', include('users.urls', namespace = 'users')),
    url(r'maps/(?P<map_type>\w+)$', maps, name = 'maps'),
    #url(r'maps_sold$', maps_sold, name = 'maps_sold'),
    url(r'plots_histograms$', plots_histograms, name = 'plots_histograms'),
    url(r'script_info$', svrea_script_info, name = 'script_info'),
    url(r'script_run$', svrea_script_run, name = 'script_run'),
    url(r'script_logs$', svrea_script_logs, name = 'script_logs'),
    url(r'script_data$', svrea_script_data, name = 'script_data')
]
