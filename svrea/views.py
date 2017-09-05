import sys

import datetime
from dateutil.relativedelta import relativedelta
import calendar
import numpy, math
from operator import itemgetter
from ratelimit.decorators import ratelimit
import logging
import json

from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models, connection
from django.db.models import Count, Max, F, Sum, Func, Avg, Q, When, Case, Value, DateTimeField, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page


from svrea_script.models import Listings, Address, GlobalVars
from svrea_etl.models import EtlListingsDaily, \
    EtlListingsWeekly, \
    EtlListingsMonthly, \
    EtlListingsQuarterly, \
    EtlListingsYearly,\
    EtlTimeSeriesFavourite,\
    EtlHistogramFavourite


class To_char(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(dtype)s')"
    utput_field = models.IntegerField()

class cast(Func):
    template = "%(expressions)s::%(dtype)s"
    if '%(dtype)s' == 'bigint':
        output_field = models.BigIntegerField()

class Extract_date(Func):
    function = 'EXTRACT'
    template = "%(function)s('%(dtype)s' from %(expressions)s)"


def gindex(request):
    return render(request, 'googleb070a3405a28a8d0.html')

@ratelimit(key='ip', rate='1/s')
def index(request):
    return redirect('maps_listings')
 #********************** do not delete this code *********************************
    # if request.POST.get('submit') == 'Log Out':
    #     logout(request)
    #     return redirect('index')
    # elif request.POST.get('submit') == 'Log In':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     user = authenticate(username=username, password=password)
    #
    #     if user is not None:
    #         login(request, user)
    #     else:
    #         messages.error(request, "Please Enter Correct User Name and Password ")
    #
    # context = {}
    # return render(request, "svrea/index.html", context=context)
#*****************************************************************************

@ratelimit(key='ip', rate='1/s')
def legal(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    context = {}
    return render(request, "svrea/legal.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
def fav_timeseries(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    if request.POST.get('runTS'):
        ts = EtlTimeSeriesFavourite.objects.values('timeseriesdict').get(id=request.POST.get('runTS').split('_')[1])['timeseriesdict']
        #print('URL PARSE', ts)
        return redirect(reverse('plots_timeseries') + '?%s' %ts)
        #return(get_plots_timeseries(ts, request))
    print()
    fav_ts = EtlTimeSeriesFavourite.objects.all().filter(username = request.user.get_username()).order_by('-creationdate')
    paginator = Paginator(fav_ts, 50, orphans=9)
    page = request.GET.get('page')

    try:
        ts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ts = paginator.page(paginator.num_pages)

    context = {
        "ts": ts
    }

    return render(request, 'svrea/fav_timeseries.html', context=context)


@login_required(redirect_field_name = "", login_url="/")
def fav_hist(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    if request.POST.get('runH'):
        hist = EtlHistogramFavourite.objects.values('histdict').get(id=request.POST.get('runH').split('_')[1])['histdict']
        return redirect(reverse('plots_hist') + '?%s' %hist)


    fav_h = EtlHistogramFavourite.objects.all().filter(username = request.user.get_username()).order_by('-creationdate')
    paginator = Paginator(fav_h, 50, orphans=9)
    page = request.GET.get('page')

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        hist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        hist = paginator.page(paginator.num_pages)

    context = {
        "hist": hist
    }

    return render(request, 'svrea/fav_histograms.html', context=context)

@ratelimit(key='ip', rate='1/s')
def plots_general(request):
    logger = logging.getLogger('testlogger')

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    period = 'Daily'
    county = 'Whole Sweden'
    property_type = 'Lägenhet'

    if request.POST:
        if request.POST.get("period"):
            period = request.POST.get("period")
            county = request.POST.get('county')
            property_type = request.POST.get('property_type')

    try:
        county_list = [county.geographic_name for county in EtlListingsDaily.objects
                                                            .filter(geographic_type__exact = 'county')
                                                            .distinct('geographic_name')
                                                            .order_by('geographic_name')]
        #print(county)
        al = EtlListingsDaily.objects
        todate = datetime.date.today()
        fromdate = todate - datetime.timedelta(days=180)
        dtype = 'YYYY-MM-DD'
        if period == 'Weekly':
            al = EtlListingsWeekly.objects
            fromdate = todate - datetime.timedelta(days = 365*4+1)
            dtype = 'YYYY-"W"IW'
        elif period == 'Monthly':
            al = EtlListingsMonthly.objects
            fromdate = todate - datetime.timedelta(days=365 * 4 + 1)
            dtype = 'YYYY-MM'
        elif period == 'Quarterly':
            al = EtlListingsQuarterly.objects
            fromdate = todate - datetime.timedelta(days=365 * 4 + 1)
            dtype = 'YYYY-"Q"Q'
        elif period == 'Yearly':
            al = EtlListingsYearly.objects
            fromdate = todate - datetime.timedelta(days=365 * 8 + 2)
            dtype = 'YYYY'
        #print(period)
        active_list = al.annotate(al = Coalesce('active_listings', 0),
                                  st = Coalesce('sold_today', 0),
                                  lpa = Coalesce('listing_price_avg', 0),
                                  lpm=Coalesce('listing_price_med', 0),
                                  spa=Coalesce('sold_price_avg', 0),
                                  spm=Coalesce('sold_price_med', 0),
                                  lpasqm=Coalesce('listing_price_sqm_avg', 0),
                                  lpmsqm=Coalesce('listing_price_sqm_med', 0),
                                  spasqm=Coalesce('sold_price_sqm_avg', 0),
                                  spmsqm=Coalesce('sold_price_sqm_med', 0)) \
            .annotate(date=To_char('record_firstdate', dtype=dtype))\
            .filter(geographic_type__exact='country' if county == 'Whole Sweden' else 'county') \
            .filter(geographic_name__exact = 'Sweden' if county == 'Whole Sweden' else county) \
            .filter(property_type = property_type)\
            .values('date',
                      'geographic_type',
                      'geographic_name',
                      'al',
                      'st',
                      'lpa',
                      'lpm',
                      'lpasqm',
                      'lpmsqm',
                      'spa',
                      'spm',
                      'spasqm',
                      'spmsqm',
                      )\
            .filter(record_firstdate__range = (fromdate, todate)) \
            .order_by('record_firstdate')

        listings = [[i['date'],                     #0
                     i['al'],          #1
                     i['st'],               #2
                     i['lpa'],        #3
                     i['lpm'],        #4
                     i['lpasqm'],    #5
                     i['lpmsqm'],    #6
                     i['spa'],           #7
                     i['spm'],           #8
                     i['spasqm'],       #9
                     i['spmsqm'],       #10
                     ] for i in active_list]

        # for q in connection.queries:
        #     print(q)

        context = {
            "success" : True,
            "county_list" : county_list,
            "period" : period,
            "active" : [['Date', 'Active Listings']] + [[i[0], i[1]] for i in listings],
            "sold": [['Date', 'Sold Today']] + [[i[0], i[2]] for i in listings],

            "listing_price": [['Date',
                               'Average',
                               'Median'
                               ]] + [[i[0], i[3], i[4]] for i in listings],

            "listing_price_sqm": [['Date',
                               'Average',
                               'Median'
                               ]] + [[i[0], i[5], i[6]] for i in listings],

            "sold_price": [['Date',
                               'Average',
                               'Median'
                               ]] + [[i[0], i[7], i[8]] for i in listings],

            "sold_price_sqm": [['Date',
                                   'Average',
                                   'Median'
                               ]] + [[i[0], i[9], i[10]] for i in listings],
            "county" : county,
            'property_type' : property_type
        }
    except Exception as e:
        logger.info(e)
        sys.stdout.flush()
        context = {
            "success" : False
        }

    return render(request, "svrea/plots_general.html", context=context)


#@login_required(redirect_field_name = "", login_url="/")
#@ratelimit(key='ip', rate='1/s')
def maps_density(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    period_type = 'Day'
    period_day = '%s' % (datetime.date.today() - datetime.timedelta(days=1))
    period_week = '%s-W%s' % (datetime.date.today().year, '0%s' % datetime.date.today().isocalendar()[1] if datetime.date.today().isocalendar()[1] < 10 else datetime.date.today().isocalendar()[1])
    period_month = '%s-%s' % (datetime.date.today().year ,'0%s' % datetime.date.today().month if datetime.date.today().month < 10 else datetime.date.today().month)
    period_quarter = '%s-Q%s' %(datetime.datetime.today().year, '1' if datetime.datetime.today().month < 4 else '2' if datetime.datetime.today().month < 7 else '3' if datetime.datetime.today().month < 10 else '4')
    period_year = '%s' % datetime.date.today().year
    # period_dayfrom = '%s' % (datetime.date.today() - datetime.timedelta(days=1))
    # period_dayto = '%s' % (datetime.date.today() - datetime.timedelta(days=1))

    map_type = 'listings'
    listingobj = EtlListingsDaily.objects
    map_date = datetime.date.today() - datetime.timedelta(days=1)
    property_type = 'Lägenhet'

    #print('request', request.POST)
    if request.POST.get('period_type'):
        #print('request', request.POST)
        period_type = request.POST.get('period_type')
        period_day = request.POST.get('period_day')
        period_week = request.POST.get('period_week')
        period_month = request.POST.get('period_month')
        period_year = request.POST.get('period_year')
        period_dayfrom = request.POST.get('period_dayfrom')
        period_dayto = request.POST.get('period_dayto')
        map_type = request.POST.get('map_type')
        property_type = request.POST.get('property_type')

    if period_type == 'Day':
        map_date = period_day
    if period_type == 'Week':
        #print(period_week)
        #datefrom = datetime.datetime.strptime(period_week + '-1', "%Y-W%W-%w")
        #dateto = datefrom + datetime.timedelta(days=7)
        listingobj = EtlListingsWeekly.objects
        map_date = datetime.datetime.strptime(period_week + '-1', "%Y-W%W-%w")
    elif period_type == 'Month':
        #datefrom = datetime.datetime.strptime(period_month + '-1', "%Y-%m-%d")
        #dateto = datefrom + datetime.timedelta(days=calendar.monthrange(datefrom.year, datefrom.month)[1])
        listingobj = EtlListingsMonthly.objects
        map_date = datetime.datetime.strptime(period_month + '-1', "%Y-%m-%d")
        #print(map_date)
    elif period_type == 'Quarter':
        listingobj = EtlListingsQuarterly.objects
        map_date = datetime.date(day=1,
                                 month=1 if period_quarter[6]=='1' else 4 if period_quarter[6] == '2' else 7 if period_quarter[6]=='3' else 10,
                                 year = int(period_quarter[:4]))
    elif period_type == 'Year':
        listingobj = EtlListingsYearly.objects
        map_date = datetime.date(day = 1,
                                 month = 1,
                                 year = int(period_year[:4]))
        #datefrom = datetime.datetime.strptime(period_year + '-01-01', "%Y-%m-%d")
        #dateto = datetime.datetime.strptime(period_year + '-12-31',
        #                                    "%Y-%m-%d") + datetime.timedelta(days=1)
    # else:  # Period
    #     datefrom = "period_dayfrom"
    #     dateto = datetime.datetime.strptime("period_dayto", '%Y-%m-%d') + datetime.timedelta(days=1)

    #ml = EtlListingsDaily.objects.filter(geographic_type__exact='municipality', record_firstdate__range = (datefrom,dateto)).values('geographic_name')
    #print(period_type, map_date)
    #print(len(listingobj))
    #print(period_type, map_date)

    ml = listingobj.filter(geographic_type__exact='municipality',
                           record_firstdate__date = map_date,
                           property_type = property_type
                           ).values('geographic_name')


    if map_type == 'listings':
        ml = ml.annotate(s = Coalesce(F('active_listings'), 0))
        text = 'Properties'
    elif map_type == 'listing_price':
        ml = ml.annotate(s = Coalesce(F('listing_price_med'), 0))
        text = 'SEK'
    elif map_type == 'listing_price_sqm':
        ml = ml.annotate(s = Coalesce(F('listing_price_sqm_med'),0))
        text = 'SEK/m<sup>2</sup>'
    elif map_type == 'sold':
        ml = ml.annotate(s = Coalesce(F('sold_today'), 0))
        text = 'Properties'
    elif map_type == 'sold_price':
        ml = ml.annotate(s = Coalesce(F('sold_price_med'), 0))
        text = 'SEK'
    elif map_type == 'sold_price_sqm':
        ml = ml.annotate(s = Coalesce(F('sold_price_sqm_med'), 0))
        text = 'SEK/m<sup>2</sup>'
    elif map_type == 'days_before_sold':
        ml = ml.annotate(s=Coalesce(F('sold_daysbeforesold_avg'), 0))
        text = 'Days'
    elif map_type == 'sold_property_age':
        ml = ml.annotate(s=Coalesce(F('sold_propertyage_avg'), 0))
        text = 'Years'
    else:
        return redirect('index')
    ml = ml.values_list('geographic_name', 's')

    #for m in ml:
    #    print(m)

    muniListings = sorted(ml, key=itemgetter(1))
    maxMuniListings = muniListings[-int(len(muniListings)/50)][1] if len(muniListings) > 0 else 0
    minMuniListings = muniListings[int(len(muniListings)/50)][1] if len(muniListings) > 0 else 0
    map_colors = [
        '#02F005', # green
        '#97FF02', # salad
        '#CDFF02', # yellow-green
        '#E8FF02', #yellow
        '#FFD102', #orange
        '#FF8402', #dark orange
        '#FF0000' #dark red
    ]



    minuListingsColors = {}
    for m in muniListings:
        a = m[1] - minMuniListings
        b = maxMuniListings - minMuniListings
        idx = int( a / b * (len(map_colors) -1 ))
        idx = 0 if idx <0 else idx
        #print(m, minMuniListings, maxMuniListings, a, b, idx
        #idx = int((m[1] -  minMuniListings) / maxMuniListings * len(map_colors))
        idx = 0 if idx < 0 else idx
        minuListingsColors[m[0]] = {"color" : map_colors[idx] if idx < len(map_colors) else '#000000',
                                    "text" : "%s %s" %(int(m[1]), text)
                                    }
    #print("SQL", connection.queries)
    context = {
        "success": False,
        "minuListingsColors" : minuListingsColors,
        "period_type" : period_type,
        "period_day" : period_day,
        "period_week": period_week,
        "period_month": period_month,
        "period_quarter": period_quarter,
        "period_year": period_year,
        "map_type" : map_type,
        "property_type" : property_type
    }


    return render(request, "svrea/maps_density.html", context=context)


def maps_listings(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")
    # ***************** only 5000 results are displayed! *************************
    listing_list = Listings.objects.filter(isactive='True').values('address__street',
                                                                   'address__house',
                                                                   'address__city',
                                                                   'address__municipality',
                                                                   'address__county',
                                                                   'latitude',
                                                                   'longitude',
                                                                   'propertytype',
                                                                   'latestprice',
                                                                   'livingarea',
                                                                   'floor'
                                                                         )[:5000]  # , booliid__exact = '2162349')
    #print(len(listing_list))

    data = []  # ['Lat', 'Long', 'tip', 'type']

    for l in listing_list:
        #print(l[:])
        saddress = "%s %s, %s, %s" % (l['address__street'],
                                      l['address__house'],
                                      (l['address__city'] if l['address__city'] == l['address__municipality']
                                       else "%s, %s" % (
                                          l['address__city'], l['address__municipality'])),
                                      l['address__county']
                                      )
        marker = 'default'

        if l['propertytype'] == 'Lägenhet':
            marker = 'lagenhet'

        if l['propertytype'] == 'Villa':
            marker = 'villa'

        tip = """%s<br/>
                %s m<sup>2</sup>, %s</br>
                %s SEK</br>
                %s

        """ % (l['propertytype'],
               l['livingarea'],
               "1st floor" if l['floor'] == '1' else "2dn floor" if l['floor']=='2' else "3rd floor" if l['floor'] == '3' else ("%sth floor" %l['floor']) if l['floor'] is not None else "",
               format(l['latestprice'], ',d') if l['latestprice'] is not None else "",
               saddress)

        data.append([float(l['latitude']),
                     float(l['longitude']),
                     tip,
                     marker
                     ])

    context = {
        "data": data,
    }

    return render(request, "svrea/maps_listings.html", context=context)


#@login_required(redirect_field_name = "", login_url="/")
@ratelimit(key='ip', rate='1/s')
def plots_histograms(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    # Add to Favourite
    if request.GET.get('save_hist') and request.user.is_authenticated():
        name = request.GET.get('name_of_hist')
        name = request.GET.get('name_of_series')
        if request.GET.get('fav_tscomment'):
            comment = request.GET.get('fav_tscomment')
        else:
            comment = None
        hist = EtlHistogramFavourite(
            creationdate = datetime.datetime.now(),
            favouritename=name,
            username=request.user.get_username(),
            comment = comment
        )
        hist.save()
        r = request.GET.copy()
        r.pop('save_hist')
        r['fav_hid'] = hist.id
        hist.histdict=r.urlencode()
        hist.save()
        messages.info(request, "%s Saved in <a href='%s'>Favourites</a>" %(name, reverse('fav_hist')))

    # Update Favourite
    if request.GET.get('update_favourite') and request.user.is_authenticated():
        id = request.GET.get('fav_hid')
        hist = EtlHistogramFavourite.objects.get(id=id)
        hist.comment = request.GET.get('fav_hcomment')
        r = request.GET.copy()
        r.pop('update_favourite')
        hist.histdict = r.urlencode()
        hist.lastupdatedate = datetime.datetime.now()
        hist.save()
        messages.info(request, "%s Was Updated in <a href='%s'>Favourites</a>" %(hist.favouritename, reverse('fav_hist')))

    #Delete Favourite
    if request.GET.get('delete_hist') and request.user.is_authenticated():
        id = request.GET.get('fav_hid')
        hist = EtlHistogramFavourite.objects.get(id=id)
        hname = hist.favouritename
        hist.delete()
        messages.info(request,"%s Was Deleted from <a href='%s'>Favourites</a>" % (hname, reverse('fav_hist')))

    # ************************  defaults  *********************

    histInfo = [{
        "property_type": "Active",
        "county_selected": ["Whole Sweden"],
        "period_type": "Day",
        "property": "Lägenhet",
        "period_day": '%s' %(datetime.date.today() - datetime.timedelta(days=1)),
        "period_week": '%s-W%s' % (datetime.date.today().year, '0%s' % datetime.date.today().isocalendar()[1] if datetime.date.today().isocalendar()[1] < 10 else datetime.date.today().isocalendar()[1]),
        "period_month": '%s-%s' % (datetime.date.today().year,'0%s' % datetime.date.today().month if datetime.date.today().month < 10 else datetime.date.today().month),
        "period_quarter": '%s-Q%s' %(datetime.date.today().year, 1 if datetime.date.today().month < 4 else 2 if datetime.date.today().month < 7 else 3 if datetime.date.today().month < 10 else 4),
        "period_year": '%s' %datetime.date.today().year,
    }]

    defHistInfo = histInfo[0] # default histInfo used to create new histograms
    hist_type = 'Price'
    chart_type = 'Column'
    data_type = ['Abs']
    num_bins = 20
    LowerCutoff = 2.5
    UpperCutoff = 100 - LowerCutoff
    g_child = 1

    # ************************** Favourite Histogram ************************************

    fav_h = None
    if request.GET.get('fav_hid') and not request.GET.get('delete_hist'):
        fav_hid = request.GET.get('fav_hid')
        fav_h = EtlHistogramFavourite.objects.get(id=fav_hid)

    #**********************************************************************************

    if request.GET.get('g_child'):
        histInfo = []
        totnum = int(request.GET.get('g_child'))
        idx = 0

        while idx < totnum:
            if not request.GET.get('index_%s' % idx):
                idx += 1
                continue

            histInfo.append({})
            histInfo[-1]['property_type'] = request.GET.get('property_type_%s' % idx)
            histInfo[-1]['county_selected'] = request.GET.getlist('county_selected_%s' % idx)
            histInfo[-1]['period_type'] = request.GET.get('period_type_%s' % idx)
            histInfo[-1]['property'] = request.GET.get('property_%s' % idx)
            histInfo[-1]['period_day'] = request.GET.get('period_day_%s' % idx)
            histInfo[-1]['period_week'] = request.GET.get('period_week_%s' % idx)
            histInfo[-1]['period_month'] = request.GET.get('period_month_%s' % idx)
            histInfo[-1]['period_quarter'] = request.GET.get('period_quater_%s' % idx)
            histInfo[-1]['period_year'] = request.GET.get('period_year_%s' % idx)
            idx += 1

        hist_type = request.GET.get('hist_type')
        chart_type = request.GET.get('chart_type')
        data_type = request.GET.getlist('data_type')
        num_bins = int(request.GET.getlist('num_bins')[0])
        LowerCutoff = float(request.GET.getlist('LowerCutoff')[0])
        UpperCutoff = float(request.GET.getlist('UpperCutoff')[0])
        g_child = request.GET.get('g_child')

    #print(hist_type)
    if hist_type == 'Price':
        formula = F('latestprice')
        filter = {'latestprice__isnull': False}
        x_axis_title = 'Price, SEK'
    elif hist_type == 'Rent':
        formula = F('rent')
        filter = {'rent__isnull': False}
        x_axis_title = 'Rent, SEK'
    elif hist_type == 'Area':
        formula = F('livingarea')
        filter = {'livingarea__isnull': False}
        x_axis_title = 'Living Area, m2'
    elif hist_type == 'Price m2':
        formula = F('latestprice')
        filter = {'latestprice__isnull': False,
                           'livingarea__isnull': False}
        x_axis_title = 'Price per m2, SEK'
    elif hist_type == 'Days Before Sold':
        formula = (Extract_date('datesold', dtype='epoch') - Extract_date('datepublished', dtype='epoch')) / (3600 * 24)
        filter = {'datesold__isnull': False}
        x_axis_title = 'Days Before Sold'
    elif hist_type == 'Property Age':
        formula = Extract_date('datesold', dtype='year') - F('constructionyear')
        filter = {'datesold__isnull': False,
                           'constructionyear__range':(1800,2100)}
        x_axis_title = 'Property Age, Yrs'
    # else:
    #     field = 'latestprice'
    #     filter_isnull_f = {'{0}__{1}'.format(field, 'isnull'): False}
    #print(formula)
    if data_type[0] == 'Rel':
        rel = True
    else:
        rel = False

    # __________________________ Generate County List _______________________

    county_list = getListOfAreas()

    # __________________________ Templates for histograms ____________________
    listings_hist = [['Price']]
    listings_list_all = []
    county_chart_all = []
    #print('histInfo:',histInfo)
    errs = 0

    for idx, hist in enumerate(histInfo):
        # ____________________ make initial QS ________________________
        if hist["property_type"] == 'Sold':
            listings_qs = Listings.objects.filter(isactive__exact=False).filter(**filter).annotate(f=ExpressionWrapper(formula,
                                                                                                  output_field=FloatField())).order_by('f')
        elif hist["property_type"] == 'Active':
            listings_qs = Listings.objects.filter(**filter).annotate(f=ExpressionWrapper(formula,
                                                                                                  output_field=FloatField())).order_by('f')
        if hist_type == 'Price m2':
            listings_qs = listings_qs.exclude(latestprice=0).exclude(livingarea=0)
        # ______________________ Deal with time ranges _______________________

        datefrom = datetime.datetime.strptime(hist["period_day"], "%Y-%m-%d")
        dateto = datefrom + datetime.timedelta(days=1)

        if hist["period_type"] == 'Week':
            datefrom = datetime.datetime.strptime(hist["period_week"] + '-1', "%Y-W%W-%w")
            dateto = datefrom + datetime.timedelta(days=7)
            # print(datefrom, dateto)
        elif hist["period_type"] == 'Month':
            datefrom = datetime.datetime.strptime(hist["period_month"] + '-1', "%Y-%m-%d")
            dateto = datefrom + datetime.timedelta(days=calendar.monthrange(datefrom.year, datefrom.month)[1])
        elif hist['period_type'] == 'Quarter':
            datefrom = datetime.date(day = 1,
                                     month = 1 if hist['period_quarter'][6] == '1' else 4 if hist['period_quarter'][6] == '2' else 7 if hist['period_quarter'][6] == '3' else 10,
                                     year = int(hist['period_quarter'][:4]))
        elif hist["period_type"] == 'Year':
            datefrom = datetime.datetime.strptime(hist["period_year"] + '-01-01', "%Y-%m-%d")
            dateto = datetime.datetime.strptime(hist["period_year"] + '-12-31', "%Y-%m-%d") + datetime.timedelta(days=1)

        listings_qs = listings_qs.filter(propertytype = hist['property'])

        if hist["property_type"] == 'Sold':
            listings_qs = listings_qs.filter(datesold__range=(datefrom, dateto))
        if hist["property_type"] == 'Active':
            listings_qs = listings_qs.annotate(di=Case(
                When(Q(dateinactive__isnull=False), then='dateinactive'),
                default=Value(datetime.date.today()),
                output_field=DateTimeField()
            )).filter(datepublished__lt=dateto, di__gte=datefrom)
        if (listings_qs.count()) == 0:
            messages.error(request, "No data for selected settings")
            errs += 1
            break

        # _____________________ Generate ordered list of all results _______________
        for idy, county in enumerate(hist["county_selected"]):
            #print('county:', county)
            if county == 'Whole Sweden':
                if hist_type == 'Price m2':
                    listings_list_all.append([int(r['latestprice'] / r['livingarea']) for r in
                                              listings_qs.values('latestprice', 'livingarea')])
                else:
                    listings_list_all.append([int(r['f']) for r in listings_qs.values('f')])
                county_chart_all.append(
                    "%s. %s(%s)" % (idx, hist["county_selected"][idy], len(listings_list_all[-1])))
            else:
                if hist_type == 'Price m2':
                    listings_list_all.append([int(r['latestprice'] / r['livingarea']) for r in
                                              listings_qs.filter(Q(address__county=county)|Q(address__municipality=county)).values(
                                                  'latestprice',
                                                  'livingarea')])
                else:
                    # print('QS:')
                    # for i in listings_qs.filter(Q(address__county=county)|Q(address__municipality=county)).values(field):
                    #     print(i)
                    listings_list_all.append(
                        [int(r['f']) for r in listings_qs.filter(Q(address__county=county)|Q(address__municipality=county)).values('f')])
                county_chart_all.append(
                    "%s. %s(%s)" % (idx, hist["county_selected"][idy], len(listings_list_all[-1])))
    # ______________________ Define highest and lowest cutoffs ____________________


    if errs == 0:
        percentH_price = numpy.percentile([int(i) for sub in listings_list_all for i in sub], UpperCutoff)
        percentL_price = numpy.percentile([int(i) for sub in listings_list_all for i in sub], LowerCutoff)
        bins = [percentL_price + (percentH_price - percentL_price) / num_bins * i for i in range(0, num_bins + 1)]

        # ______________________ label X axis with bins __________________________

        listings_hist.append(["<%s" % "{0:,}".format(int(percentL_price))])

        for idx, p in enumerate(bins):
            if idx == len(bins) - 1:
                break
            listings_hist.append(["{0:,}".format(int((p + bins[idx + 1]) / 2))])

        listings_hist.append([">%s" % "{0:,}".format(int(percentH_price))])

        # _______________________ fill Y axis with histograms ________________________

        for idx, (listings_list, county) in enumerate(zip(listings_list_all, county_chart_all)):
            hist = numpy.histogram(listings_list, bins=bins)
            listings_hist[0].append('%s' % county)
            tot = len(listings_list)
            listings_hist[1].append(len([n for n in listings_list if n < percentL_price]) / (tot if rel else 1))

            for i, h in enumerate(hist[0]):
                listings_hist[i + 2].append(h / (tot if rel else 1))

            listings_hist[-1].append(len([n for n in listings_list if n > percentH_price]) / (tot if rel else 1))
    #print(connection.queries)
    context = {"histInfo": histInfo,
               "defHistInfo": defHistInfo,
               "county_list": county_list,
               "hist_type": hist_type,
               "chart_type": chart_type,
               "data_type": data_type[0],
               "listings_hist": listings_hist,
               "x_axis_title": x_axis_title,
               "num_bins": num_bins,
               "LowerCutoff": LowerCutoff,
               "UpperCutoff": UpperCutoff,
               "g_child": g_child,
               "fav_h" : fav_h
               }

    return render(request, "svrea/plots_histograms.html", context=context)


@ratelimit(key='ip', rate='1/s')
def plots_timeseries(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')
    elif request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")

    # Add to Favourite
    if request.GET.get('save_series') and request.user.is_authenticated():
        name = request.GET.get('name_of_series')
        if request.GET.get('fav_tscomment'):
            comment = request.GET.get('fav_tscomment')
        else:
            comment = None
        ts = EtlTimeSeriesFavourite(
            creationdate=datetime.datetime.now(),
            favouritename=name,
            username=request.user.get_username(),
            comment = comment
        )
        ts.save()
        r = request.GET.copy()
        r.pop('save_series')
        r['fav_tsid'] = ts.id
        ts.timeseriesdict=r.urlencode()
        ts.save()
        messages.info(request, "%s Saved in <a href='%s'>Favourites</a>" %(name, reverse('fav_timeseries')))

    # Update Favourite
    if request.GET.get('update_favourite') and request.user.is_authenticated():
        id = request.GET.get('fav_tsid')
        ts = EtlTimeSeriesFavourite.objects.get(id=id)
        ts.comment = request.GET.get('fav_tscomment')
        r = request.GET.copy()
        r.pop('update_favourite')
        ts.timeseriesdict = r.urlencode()
        ts.lastupdatedate = datetime.datetime.now()
        ts.save()
        messages.info(request, "%s Was Updated in <a href='%s'>Favourites</a>" %(ts.favouritename, reverse('fav_timeseries')))

    #Delete Favourite
    if request.GET.get('delete_series') and request.user.is_authenticated():
        id = request.GET.get('fav_tsid')
        ts = EtlTimeSeriesFavourite.objects.get(id=id)
        tsname = ts.favouritename
        ts.delete()
        messages.info(request,"%s Was Deleted from <a href='%s'>Favourites</a>" % (tsname, reverse('fav_timeseries')))


    # ************************  defaults  *********************
    time_series = [{ # this is a list containing info about all time series
        "ts_type": "Active",
        "p_type" : 'Lägenhet',
        "county_selected": ["Whole Sweden"],
    }]

    period_to = datetime.date.today()
    period_from = period_to - datetime.timedelta(days = 180)
    period_step = 'Day'
    data_type = 'Number'
    qs = EtlListingsDaily.objects
    dtype = 'YYYY-MM-DD'
    chart_type = 'Line'
    #data_rep = 'Abs'
    y_axis_title = 'Number of properties'
    g_child = 1

    # **********************************************************
    fav_ts = None
    if request.GET.get('fav_tsid') and not request.GET.get('delete_series'):
        fav_tsid = request.GET.get('fav_tsid')
        fav_ts = EtlTimeSeriesFavourite.objects.get(id=fav_tsid)

    #**************************************************************
    if request.GET.get('g_child'):  # if GET, then ignore defaults
        #print(request.POST)
        time_series = []
        totnum = int(request.GET.get('g_child'))
        idx = 0

        while idx < totnum:
            if not request.GET.get('index_%s' % idx):
                idx += 1
                continue
            time_series.append({})
            time_series[-1]['ts_type'] = request.GET.get('ts_type_%s' % idx)
            time_series[-1]['p_type'] = request.GET.get('p_type_%s' % idx)
            time_series[-1]['county_selected'] = request.GET.getlist('county_selected_%s' % idx)
            idx += 1

        period_to = datetime.datetime.strptime(request.GET.get('period_to'),'%Y-%m-%d')
        period_from = datetime.datetime.strptime(request.GET.get('period_from'),'%Y-%m-%d')
        period_step = request.GET.get('period_step')

        if period_step == 'Week':
            qs = EtlListingsWeekly.objects
            dtype = 'YYYY-"W"IW'
            # find monday of this week
            while period_from.weekday() != 0:
                period_from -= datetime.timedelta(days=1)
        elif period_step == 'Month':
            qs = EtlListingsMonthly.objects
            dtype = 'YYYY-MM'
            period_from = period_from.replace(day = 1)
        elif period_step == 'Quarter':
            qs = EtlListingsQuarterly.objects
            dtype = 'YYYY-"Q"Q'
            if period_from.month < 4:
                period_from = period_from.replace(day = 1, month = 1)
            elif period_from.month < 7:
                period_from = period_from.replace(day = 1, month = 3)
            elif period_from.month < 10:
                period_from = period_from.replace(day = 1, month = 6)
            elif period_from.month < 13:
                period_from = period_from.replace(day = 1, month = 9)
        elif period_step == 'Year':
            qs = EtlListingsYearly.objects
            dtype = 'YYYY'
            period_from = period_from.replace(day = 1, month = 1)

        data_type = request.GET.get('data_type')

        chart_type = request.GET.get('chart_type')
        g_child = request.GET.get('g_child')

    if data_type == 'Number':
        y_axis_title = 'Number of properties'
    elif data_type == 'Price':
        y_axis_title = 'Price, SEK'
    elif data_type == 'Price m2':
        y_axis_title = 'Price / m2, SEK'
    elif data_type == 'Area':
        y_axis_title = 'Living area, m2'
    elif data_type == 'Rent':
        y_axis_title = 'Rent per month, SEK'
    elif data_type == 'Days Before Sold':
        y_axis_title = 'Days Before Sold'
    elif data_type == 'Property Age':
        y_axis_title = 'Property Age'


    # __________________________ Generate County List _______________________

    county_list = getListOfAreas()

    # ______________________________________________

    ts_data = [['haxis']]

    qs = qs.filter(record_firstdate__gte = period_from,
                    record_firstdate__lte = period_to)
    qts = qs.annotate(date=To_char('record_firstdate', dtype=dtype))\
        .values('date').distinct().order_by('record_firstdate')

    #print('qts', len(qts))
    for t in qts:
        ts_data.append([t['date']])
#        xaxis.append(t['record_firstdate'])

    for ts in time_series:
        for county in ts['county_selected']:
            if county == 'Whole Sweden':
                county = 'Sweden'
            qqs = qs
            qqs = qqs.filter(geographic_name = county, property_type = ts['p_type'])

            #print('qqs', len(qqs))

            if ts['ts_type'] == 'Active':
                if data_type == 'Number':
                    qqs = qqs.annotate(p=Coalesce('active_listings', 0)) \
                        .values('record_firstdate', 'p')
                elif data_type == 'Price':
                    qqs = qqs.annotate(p=Coalesce('listing_price_med', 0))\
                        .values('record_firstdate','p')
                elif data_type == 'Price m2':
                    qqs = qqs.annotate(p=Coalesce('listing_price_sqm_med', 0)) \
                        .values('record_firstdate','p')
                elif data_type == 'Area':
                    qqs = qqs.annotate(p=Coalesce('listing_area_med', 0)).values('record_firstdate','p')
                elif data_type == 'Rent':
                    qqs = qqs.annotate(p=Coalesce('listing_rent_med', 0)).values('record_firstdate','p')
                elif data_type == 'Days Before Sold':
                    qqs = qqs.annotate(p=Coalesce('sold_daysbeforesold_avg', 0)).values('record_firstdate','p')
                elif data_type == 'Property Age':
                    qqs = qqs.annotate(p=Coalesce('sold_propertyage_avg', 0)).values('record_firstdate','p')
            elif ts['ts_type'] == 'Sold':
                if data_type == 'Number':
                    qqs = qqs.annotate(p=Coalesce('sold_today', 0)) \
                        .values('record_firstdate', 'p')
                elif data_type == 'Price':
                    qqs = qqs.annotate(p=Coalesce('sold_price_med', 0)) \
                        .values('record_firstdate','p')
                elif data_type == 'Price m2':
                    qqs = qqs.annotate(p=Coalesce('sold_price_sqm_med', 0)) \
                        .values('record_firstdate','p')
                elif data_type == 'Area':
                    qqs = qqs.annotate(p=Coalesce('sold_area_med', 0)).values('record_firstdate','p')
                elif data_type == 'Rent':
                    qqs = qqs.annotate(p=Coalesce('sold_rent_med', 0)).values('record_firstdate','p')
                elif data_type == 'Days Before Sold':
                    qqs = qqs.annotate(p=Coalesce('sold_daysbeforesold_avg', 0)).values('record_firstdate','p')
                elif data_type == 'Property Age':
                    qqs = qqs.annotate(p=Coalesce('sold_propertyage_avg', 0)).values('record_firstdate','p')

            qqs = qqs.order_by('record_firstdate')
            ts_data[0].append('%s, %s, %s, %s' % (county, ts['p_type'], ts['ts_type'], data_type))
            #print(qqs)

            #print('PRINT', len(qqs), len(ts_data))
            for idx in range (0,len(qqs)):
                #print(idx, qqs[idx])
                ts_data[idx+1].append(float(qqs[idx]['p']))

    #print(time_series)

    context = {"ts_data":ts_data,
                "period_to" : period_to.strftime('%Y-%m-%d'),
                "period_from" : period_from.strftime('%Y-%m-%d'),
                "period_step" : period_step,
                "data_type" : data_type,
               "chart_type": chart_type,
               #"data_rep": data_rep,
               "time_series": time_series,
               "county_list": county_list,
               "x_axis_title": period_step,
               "y_axis_title": y_axis_title,
               "g_child": g_child,
               "fav_ts" : fav_ts,
               }
    #print(context)
    return render(request, "svrea/plots_timeseries.html", context=context)


def getListOfAreas():
    return GlobalVars.objects.get(var='list_of_areas').dicval

    # list_of_areas = {'Whole Sweden' : {}}
    #
    #
    # for county in Address.objects.distinct('county').order_by('county').values('county'):
    #     if county['county'] is not None:
    #         list_of_areas['Whole Sweden']['%s' %county['county']] = []
    #
    #         for muni in Address.objects.filter(county = county['county']).distinct('municipality').order_by('municipality').values('municipality'):
    #             if muni['municipality'] is not None:
    #                 list_of_areas['Whole Sweden']['%s' %county['county']].append(muni['municipality'])
    #
    # var = GlobalVars.objects.get_or_create(var = 'list_of_',
    #                                        defaults = {
    #                                            'dicval': list_of_areas
    #                                        })
    # return list_of_areas






