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
    listings_map,
    density_map,
    price_density_map,
    plots_histograms
)

from svrea_script.views import script_history as svrea_script_history
from svrea_script.views import script_run as svrea_script_run
from svrea_script.views import script_logs as svrea_script_logs

from uauth.views import uregister

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name = 'index'),
    url(r'^register/', uregister, name = 'register'),
    url(r'^users/', include('users.urls', namespace = 'users')),
    url(r'listings_map$', listings_map, name = 'listings_map'),
    url('density_map$', density_map, name = 'density_map'),
    url(r'price_density_map$', price_density_map, name = 'price_density_map'),
    url(r'plots_histograms$', plots_histograms, name = 'plots_histograms'),
    url(r'script_history$', svrea_script_history, name = 'script_history'),
    url(r'script_run$', svrea_script_run, name = 'script_run'),
    url(r'script_loga$', svrea_script_logs, name = 'script_logs')
]
