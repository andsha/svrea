import sys

import datetime
from dateutil.relativedelta import relativedelta
import calendar
import numpy, math
from operator import itemgetter
from ratelimit.decorators import ratelimit

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models, connection
from django.db.models import Count, Max, F, Sum, Func, Avg, Q, When, Case, Value, DateTimeField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from svrea_script.models import Listings, Address
from svrea_etl.models import EtlListingsDaily, \
    EtlListingsWeekly, \
    EtlListingsMonthly, \
    EtlListingsQuaterly, \
    EtlListingsYearly,\
    EtlTimeSeriesFavourite


class To_char(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(dtype)s')"
    utput_field = models.IntegerField()

class cast(Func):
    template = "%(expressions)s::%(dtype)s"
    if '%(dtype)s' == 'bigint':
        output_field = models.BigIntegerField()


def gindex(request):
    return render(request, 'googleb070a3405a28a8d0.html')

@ratelimit(key='ip', rate='1/s')
def index(request):
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
    return render(request, "svrea/index.html", context=context)


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

    # if request.POST.get('deleteInfo'):
    #     infoid = request.POST.get('deleteInfo').split('_')[1]
    #     num = Info.objects.get(id=infoid).delete()

    fav_ts = EtlTimeSeriesFavourite.objects.all().order_by('-creationdate')
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
        "info": ts
    }

    return render(request, 'svrea/fav_timeseries.html', context=context)


@ratelimit(key='ip', rate='1/s')
def plots_general(request):

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

    if request.POST:
        if request.POST.get("period"):
            period = request.POST.get("period")
        if request.POST.get('county'):
            county = request.POST.get('county')

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
        elif period == 'Quaterly':
            al = EtlListingsQuaterly.objects
            fromdate = todate - datetime.timedelta(days=365 * 4 + 1)
            dtype = 'YYYY-"Q"Q'
        elif period == 'Yearly':
            al = EtlListingsYearly.objects
            fromdate = todate - datetime.timedelta(days=365 * 8 + 2)
            dtype = 'YYYY'
        #print(period)
        active_list = al.annotate(al = Coalesce('active_listings', 0),st = Coalesce('sold_today', 0)) \
            .annotate(date=To_char('record_firstdate', dtype=dtype))\
            .filter(geographic_type__exact='country' if county == 'Whole Sweden' else 'county') \
            .filter(geographic_name__exact = 'Sweden' if county == 'Whole Sweden' else county) \
            .values('date',
                      'geographic_type',
                      'geographic_name',
                      'al',
                      'st',
                      'listing_price_avg',
                      'listing_price_med',
                      'listing_price_sqm_avg',
                      'listing_price_sqm_med',
                      'sold_price_avg',
                      'sold_price_med',
                      'sold_price_sqm_avg',
                      'sold_price_sqm_med',
                      )\
            .filter(record_firstdate__range = (fromdate, todate)) \
            .order_by('record_firstdate')

        listings = [[i['date'],                     #0
                     i['al'],          #1
                     i['st'],               #2
                     i['listing_price_avg'],        #3
                     i['listing_price_med'],        #4
                     i['listing_price_sqm_avg'],    #5
                     i['listing_price_sqm_med'],    #6
                     i['sold_price_avg'],           #7
                     i['sold_price_med'],           #8
                     i['sold_price_sqm_avg'],       #9
                     i['sold_price_sqm_med'],       #10
                     ] for i in active_list]

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
            "county" : county
        }
    except Exception as e:
        print(e)
        sys.stdout.flush()
        context = {
            "success" : False
        }
    return render(request, "svrea/plots_general.html", context=context)


#@login_required(redirect_field_name = "", login_url="/")
@ratelimit(key='ip', rate='1/s')
def maps(request):

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
    period_week = '%s-W%s' % (datetime.date.today().year, '0%s' % datetime.date.today().isocalendar()[1] if
    datetime.date.today().isocalendar()[1] < 10 else datetime.date.today().isocalendar()[1])
    period_month = '%s-%s' % (datetime.date.today().year
                               ,'0%s' % datetime.date.today().month if datetime.date.today().month < 10 else datetime.date.today().month)
    period_year = '%s' % datetime.date.today().year
    period_dayfrom = '%s' % (datetime.date.today() - datetime.timedelta(days=1))
    period_dayto = '%s' % (datetime.date.today() - datetime.timedelta(days=1))

    map_type = 'listings'

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

    #print(period_type)
    if period_type == 'Day':
        datefrom = datetime.datetime.strptime(period_day, "%Y-%m-%d")
        dateto = datefrom + datetime.timedelta(days=1)
    elif period_type == 'Week':
        #print(period_week)
        datefrom = datetime.datetime.strptime(period_week + '-1', "%Y-W%W-%w")
        dateto = datefrom + datetime.timedelta(days=7)
        #print(datefrom, dateto)
    elif period_type == 'Month':
        datefrom = datetime.datetime.strptime(period_month + '-1', "%Y-%m-%d")
        dateto = datefrom + datetime.timedelta(days=calendar.monthrange(datefrom.year, datefrom.month)[1])
    elif period_type == 'Year':
        datefrom = datetime.datetime.strptime(period_year + '-01-01', "%Y-%m-%d")
        dateto = datetime.datetime.strptime(period_year + '-12-31',
                                            "%Y-%m-%d") + datetime.timedelta(days=1)
    else:  # Period
        datefrom = "period_dayfrom"
        dateto = datetime.datetime.strptime("period_dayto", '%Y-%m-%d') + datetime.timedelta(days=1)

    ml = EtlListingsDaily.objects.filter(geographic_type__exact='municipality', record_firstdate__range = (datefrom,dateto)).values('geographic_name')

    if map_type == 'listings':
        ml = ml.annotate(s=Avg('active_listings'))
        text = 'Properties'
    elif map_type == 'listing_price':
        ml = ml.annotate(s=Sum(cast('active_listings', dtype = 'bigint') * F('listing_price_med')) / Sum('active_listings'))
        text = 'SEK'
    elif map_type == 'listing_price_sqm':
        ml = ml.annotate(s=Coalesce(Sum(cast('active_listings', dtype='bigint') * F('listing_price_med')),0) / Coalesce(Sum(cast('active_listings', dtype='bigint') * F('listing_area_avg')),1))
        text = 'SEK/m<sup>2<sup>'
    elif map_type == 'sold':
        ml = ml.annotate(s = Sum('sold_today'))
        text = 'Properties'
    elif map_type == 'sold_price':
        ml = ml.annotate(s=Coalesce(Sum(cast('sold_today', dtype = 'bigint') * F('sold_price_med')) / Sum('sold_today'), 0))
        text = 'SEK'
    elif map_type == 'sold_price_sqm':
        ml = ml.annotate(s=Coalesce(Sum(cast('sold_today', dtype='bigint') * F('sold_price_med')), 0) / Coalesce(Sum(cast('sold_today', dtype='bigint') * F('sold_area_avg')), 1))
        text = 'SEK/m<sup>2<sup>'
    else:
        return redirect('index')
    ml = ml.values_list('geographic_name', 's')

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

    context = {
        "success": False,
        "minuListingsColors" : minuListingsColors,
        "period_type" : period_type,
        "period_day" : period_day,
        "period_week": period_week,
        "period_month": period_month,
        "period_year": period_year,
        "period_dayfrom": period_dayfrom,
        "period_dayto": period_dayto,
        "map_type" : map_type
    }

    return render(request, "svrea/maps.html", context=context)


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

    skip = False
    # numHist = 0
    histInfo = [{
        "property_type": "Listings",
        "county_selected": ["Whole Sweden"],
        "period_type": "Day",
        "period_day": '%s' % (datetime.date.today() - datetime.timedelta(days=1)),
        "period_week": '%s-W%s' % (datetime.date.today().year, '0%s' % datetime.date.today().isocalendar()[1] if
        datetime.date.today().isocalendar()[1] < 10 else datetime.date.today().isocalendar()[1]),
        "period_month": '%s-%s' % (datetime.date.today().year,
                                   '0%s' % datetime.date.today().month if datetime.date.today().month < 10 else datetime.date.today().month),
        "period_year": '%s' % datetime.date.today().year,
        "period_dayfrom": '%s' % (datetime.date.today() - datetime.timedelta(days=1)),
        "period_dayto": '%s' % (datetime.date.today() - datetime.timedelta(days=1))
    }]

    defHistInfo = histInfo[0]

    # property_type = 'listings'
    # county_selected = 'Whole Sweden'
    hist_type = 'Price'
    chart_type = 'Column'
    data_type = ['Abs']
    num_bins = 20
    LowerCutoff = 2.5
    UpperCutoff = 100 - LowerCutoff
    g_child = 1

    if request.POST.get('g_child'):
        histInfo = []

        # for idx in range(0, int(request.POST.get('g_numHist'))):
        totnum = int(request.POST.get('g_child'))
        idx = 0
        while idx < totnum:
            if not request.POST.get('index_%s' % idx):
                idx += 1
                continue

            histInfo.append({})
            histInfo[-1]['property_type'] = request.POST.get('property_type_%s' % idx)
            histInfo[-1]['county_selected'] = request.POST.getlist('county_selected_%s' % idx)
            histInfo[-1]['period_type'] = request.POST.get('period_type_%s' % idx)
            histInfo[-1]['period_day'] = request.POST.get('period_day_%s' % idx)
            histInfo[-1]['period_week'] = request.POST.get('period_week_%s' % idx)
            histInfo[-1]['period_month'] = request.POST.get('period_month_%s' % idx)
            histInfo[-1]['period_year'] = request.POST.get('period_year_%s' % idx)
            histInfo[-1]['period_dayfrom'] = request.POST.get('period_dayfrom_%s' % idx)
            histInfo[-1]['period_dayto'] = request.POST.get('period_dayto_%s' % idx)
            idx += 1

        hist_type = request.POST.get('hist_type')
        chart_type = request.POST.get('chart_type')
        data_type = request.POST.getlist('data_type')
        num_bins = int(request.POST.getlist('num_bins')[0])
        LowerCutoff = float(request.POST.getlist('LowerCutoff')[0])
        UpperCutoff = float(request.POST.getlist('UpperCutoff')[0])
        g_child = request.POST.get('g_child')

    if hist_type == 'Price':
        field = 'latestprice'
        filter_isnull_f = {'{0}__{1}'.format(field, 'isnull'): False}
        x_axis_title = 'Price, SEK'
    elif hist_type == 'Rent':
        field = 'rent'
        filter_isnull_f = {'{0}__{1}'.format(field, 'isnull'): False}
        x_axis_title = 'Rent, SEK'
    elif hist_type == 'Area':
        field = 'livingarea'
        filter_isnull_f = {'{0}__{1}'.format(field, 'isnull'): False}
        x_axis_title = 'Living Area, m2'
    elif hist_type == 'Price m2':
        field = 'latestprice'
        filter_isnull_f = {'{0}__{1}'.format('latestprice', 'isnull'): False,
                           '{0}__{1}'.format('livingarea', 'isnull'): False}
        x_axis_title = 'Price per m2, SEK'
    else:
        field = 'latestprice'
        filter_isnull_f = {'{0}__{1}'.format(field, 'isnull'): False}

    if data_type[0] == 'Rel':
        rel = True
    else:
        rel = False

    # __________________________ Generate County List _______________________

    county_list = ['Whole Sweden']

    for i in [address.county for address in Address.objects.filter(listings__isactive__exact=True)
            .distinct('county')
            .order_by('county')]:
        county_list.append(i)

    #print(connection.queries)
    # __________________________ Templates for histograms ____________________
    listings_hist = [['Price']]
    listings_list_all = []
    county_chart_all = []
    #print("there",connection.queries)
    for idx, hist in enumerate(histInfo):
        # ____________________ make initial QS ________________________
        if hist["property_type"] == 'Sold':
            listings_qs = Listings.objects.filter(isactive__exact=False).filter(**filter_isnull_f).order_by(
                field)
        elif hist["property_type"] == 'Listings':
            listings_qs = Listings.objects.filter(**filter_isnull_f).order_by(field)
        if hist_type == 'Price m2':
            listings_qs = listings_qs.exclude(latestprice=0).exclude(livingarea=0)
        # ______________________ Deal with time ranges _______________________
        if hist["period_type"] == 'Day':
            datefrom = datetime.datetime.strptime(hist["period_day"], "%Y-%m-%d")
            dateto = datefrom + datetime.timedelta(days=1)
        elif hist["period_type"] == 'Week':
            datefrom = datetime.datetime.strptime(hist["period_week"] + '-1', "%Y-W%W-%w")
            dateto = datefrom + datetime.timedelta(days=7)
            # print(datefrom, dateto)
        elif hist["period_type"] == 'Month':
            datefrom = datetime.datetime.strptime(hist["period_month"] + '-1', "%Y-%m-%d")
            dateto = datefrom + datetime.timedelta(days=calendar.monthrange(datefrom.year, datefrom.month)[1])
        elif hist["period_type"] == 'Year':
            datefrom = datetime.datetime.strptime(hist["period_year"] + '-01-01', "%Y-%m-%d")
            dateto = datetime.datetime.strptime(hist["period_year"] + '-12-31',                                                "%Y-%m-%d") + datetime.timedelta(days=1)
        else:  # Period
            datefrom = hist["period_dayfrom"]
            dateto = datetime.datetime.strptime(hist["period_dayto"], '%Y-%m-%d') + datetime.timedelta(days=1)
        if hist["property_type"] == 'Sold':
            listings_qs = listings_qs.filter(datesold__range=(datefrom, dateto))
        if hist["property_type"] == 'Listings':
            listings_qs = listings_qs.annotate(di=Case(
                When(Q(dateinactive__isnull=False), then='dateinactive'),
                default=Value(datetime.date.today()),
                output_field=DateTimeField()
            )).filter(datepublished__lt=dateto, di__gte=datefrom)
        if (listings_qs.count()) == 0:
            messages.error(request, "No data for selected settings")
            break
        # _____________________ Generate ordered list of all results _______________
        for idy, county in enumerate(hist["county_selected"]):
            if county == 'Whole Sweden':
                if hist_type == 'Price m2':
                    listings_list_all.append([int(r['latestprice'] / r['livingarea']) for r in
                                              listings_qs.values('latestprice', 'livingarea')])
                else:
                    listings_list_all.append([int(r[field]) for r in listings_qs.values(field)])
                county_chart_all.append(
                    "%s. %s(%s)" % (idx, hist["county_selected"][idy], len(listings_list_all[-1])))
            else:
                if hist_type == 'Price m2':
                    listings_list_all.append([int(r['latestprice'] / r['livingarea']) for r in
                                              listings_qs.filter(address__county=county).values(
                                                  'latestprice',
                                                  'livingarea')])
                else:
                    listings_list_all.append(
                        [int(r[field]) for r in listings_qs.filter(address__county=county).values(field)])
                county_chart_all.append(
                    "%s. %s(%s)" % (idx, hist["county_selected"][idy], len(listings_list_all[-1])))
    # ______________________ Define highest and lowest cutoffs ____________________

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

    # save time series in favourites
    # print('POST')
    # print(request.POST)
    # print(request.POST.get('save_series') and request.user.is_authenticated())
    # print('END')
    if request.POST.get('save_series') and request.user.is_authenticated():
        name = request.POST.get('name_of_series')
        ts = EtlTimeSeriesFavourite(
            creationdate = datetime.date.today(),
            favouritename = name,
            username = request.user.get_username(),
            timeseriesdict = dict(request.POST)
        )
        ts.save()
        messages.info(request, "Time series %s saved in favourites" %name)

    # ************************  defaults  *********************
    time_series = [{ # this is a list containing info about all time series
        "ts_type": "Active",
        "county_selected": ["Whole Sweden"],
    }]

    period_to = datetime.date.today()
    period_from = period_to - datetime.timedelta(days = 180)
    period_step = 'Day'
    data_type = 'Number'
    qs = EtlListingsDaily.objects
    dtype = 'YYYY-MM-DD'
    chart_type = 'Line'
    data_rep = 'Abs'
    y_axis_title = 'Number of properties'
    g_child = 1


    # **********************************************************
    #print(request.POST)
    if request.POST.get('g_child'):  # if post, then ignore defaults
        #print(request.POST)
        time_series = []
        totnum = int(request.POST.get('g_child'))
        idx = 0

        while idx < totnum:
            if not request.POST.get('index_%s' % idx):
                idx += 1
                continue
            time_series.append({})
            time_series[-1]['ts_type'] = request.POST.get('ts_type_%s' % idx)
            time_series[-1]['county_selected'] = request.POST.getlist('county_selected_%s' % idx)
            idx += 1

        period_to = datetime.datetime.strptime(request.POST.get('period_to'),'%Y-%m-%d')
        period_from = datetime.datetime.strptime(request.POST.get('period_from'),'%Y-%m-%d')
        period_step = request.POST.get('period_step')

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
        elif period_step == 'Quater':
            qs = EtlListingsQuaterly.objects
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

        data_type = request.POST.get('data_type')

        chart_type = request.POST.get('chart_type')
        data_rep = request.POST.getlist('data_rep')
        g_child = request.POST.get('g_child')

    if data_type == 'Number':
        y_axis_title = 'Number of properties'
    elif data_type == 'Price':
        y_axis_title = 'Price, SEK'
    if data_type == 'Price m2':
        y_axis_title = 'Price / <sup>m2</sup>, SEK'

    if data_rep == 'Rel':
        rel = True
    else:
        rel = False

    # __________________________ Generate County List _______________________

    county_list = ['Whole Sweden']

    for i in [address.county for address in Address.objects.distinct('county').order_by('county')]:
        county_list.append(i)

    # ______________________________________________

    ts_data = [['haxis']]

    qs = qs.filter(record_firstdate__gte = period_from,
                    record_firstdate__lte = period_to)
    qts = qs.annotate(date=To_char('record_firstdate', dtype=dtype))\
        .values('date').distinct().order_by('record_firstdate')

    for t in qts:
        ts_data.append([t['date']])
#        xaxis.append(t['record_firstdate'])

    for ts in time_series:
        for county in ts['county_selected']:
            if county == 'Whole Sweden':
                county = 'Sweden'
            qqs = qs
            qqs = qqs.filter(geographic_name = county)

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

            qqs = qqs.order_by('record_firstdate')
            ts_data[0].append('%s, %s, %s' % (county, ts['ts_type'], data_type))
            #print(ts_data)

            #print(qqs)
            for idx in range (0,len(qqs)):
                #print(idx, qqs[idx])
                ts_data[idx+1].append(qqs[idx]['p'])

    #print(period_to)

    context = {"ts_data":ts_data,
                "period_to" : period_to.strftime('%Y-%m-%d'),
                "period_from" : period_from.strftime('%Y-%m-%d'),
                "period_step" : period_step,
                "data_type" : data_type,
               "chart_type": chart_type,
               "data_rep": data_rep,
               "time_series": time_series,
               "county_list": county_list,
               "x_axis_title": period_step,
               "y_axis_title": y_axis_title,
               "g_child": g_child,
               }
    #print(context)


    return render(request, "svrea/plots_timeseries.html", context=context)


