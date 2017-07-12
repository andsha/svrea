import sys

import datetime
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


from svrea_script.models import Listings, Address
from svrea_etl.models import EtlListingsDaily




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
        active_list = EtlListingsDaily.objects.annotate(al = Coalesce('active_listings', 0),st = Coalesce('sold_today', 0)) \
            .filter(geographic_type__exact='country' if county == 'Whole Sweden' else 'county') \
            .filter(geographic_name__exact = 'Sweden' if county == 'Whole Sweden' else county) \
            .values('record_date',
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
                      )
#        print ([i for i in active_list])
#         if county == 'Whole Sweden':
#             active_list = active_list.filter(geographic_name__exact = county)

        #listings = []
        #print(active_listings_period)
        #for idx in range(0,2):
        # idx = 0: current_listings
        # idx = 1: sold_today
        to_date = datetime.date.today()
        if period == 'Daily':
            dtype = 'YYYY-MM-DD'
            from_date = to_date - datetime.timedelta(days = 180)
        elif period == 'Monthly':
            dtype =  'YYYY-MM'
            from_date = to_date - datetime.timedelta(weeks=208)
        elif period == 'Weekly':
            dtype = 'YYYY-"W"IW'
            from_date = to_date - datetime.timedelta(weeks=208)
        elif period == 'Yearly':
            dtype = 'YYYY'
            from_date = to_date - datetime.timedelta(weeks=520)
        else:
            dtype = 'YYYY'
            from_date = to_date - datetime.timedelta(weeks=520)
        #print(from_date, to_date)
        listings = [[i['date'],                     #0
                     i['active_listings'],          #1
                     i['sold_today'],               #2
                     i['listing_price_avg'],        #3
                     i['listing_price_med'],        #4
                     i['listing_price_sqm_avg'],    #5
                     i['listing_price_sqm_med'],    #6
                     i['sold_price_avg'],           #7
                     i['sold_price_med'],           #8
                     i['sold_price_sqm_avg'],       #9
                     i['sold_price_sqm_med'],       #10
                     ] for i in (active_list.filter(record_date__range = (from_date, to_date))
                                                            .annotate(date = To_char('record_date', dtype = dtype))
                                                            .values('date')
                                                            .annotate(active_listings = Sum(Coalesce('active_listings', 0)) / Count(To_char('record_date', dtype = 'YYYY-MM-DD'), distinct=True),
                                                                      sold_today = Sum(Coalesce('sold_today', 0)),
                                                                      listing_price_avg = Avg('listing_price_avg'),
                                                                      listing_price_med = Avg('listing_price_med'),
                                                                      listing_price_sqm_avg = Avg('listing_price_sqm_avg'),
                                                                      listing_price_sqm_med = Avg('listing_price_sqm_med'),
                                                                      sold_price_avg=Avg(Coalesce('sold_price_avg', 0)),
                                                                      sold_price_med=Avg(Coalesce('sold_price_med', 0)),
                                                                      sold_price_sqm_avg = Avg(Coalesce('sold_price_sqm_avg', 0)),
                                                                      sold_price_sqm_med = Avg(Coalesce('sold_price_sqm_med', 0)),
                                                                      )
                                                            .order_by('date'))]


        context = {
            "success" : True,
            "county_list" : county_list,
            "period" : period,
            "current_listings" : [['Date', 'Active Listings']] + [[i[0], i[1]] for i in listings],
            "sold_listings": [['Date', 'Sold Today']] + [[i[0], i[2]] for i in listings],
            #"listing_price" : [[i[0], i[5], i[5], i[6], i[6]] for i in listings],

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

    print(period_type)
    if period_type == 'Day':
        datefrom = datetime.datetime.strptime(period_day, "%Y-%m-%d")
        dateto = datefrom + datetime.timedelta(days=1)
    elif period_type == 'Week':
        #print(period_week)
        datefrom = datetime.datetime.strptime(period_week + '-1', "%Y-W%W-%w")
        dateto = datefrom + datetime.timedelta(days=7)
        print(datefrom, dateto)
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



    # field = ''
    # if map_type == 'listings':
    #     field = 'active_listings'
    #     text = 'active listings'
    # elif map_type == 'listing_price':
    #     field = 'listing_price_med'
    #     text = 'active listings median price'
    # elif map_type == 'listing_price_sqm':
    #     field = 'listing_price_sqm_med'
    #     text = 'active listings median price per m<sup>2<sup>'
    # elif map_type == 'sold':
    #     field = 'sold_today'
    #     text = 'properties sold'
    # elif map_type == 'sold_price':
    #     field = 'sold_price_med'
    #     text = 'sold property median price'
    # elif map_type == 'sold_price_sqm':
    #     field = 'sold_price_sqm_med'
    #     text = 'sold property median price per m<sup>2<sup>'
    # else:
    #     return redirect('index')

    ml = EtlListings.objects.filter(geographic_type__exact='municipality', record_date__range = (datefrom,dateto)).values('geographic_name')

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

    print(ml)
    #for m in ml:
        #print(m)
        #print(datefrom, dateto)

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
    # period_type = 'Day'
    # period_day =
    # period_week = '%s-W%s' %(datetime.date.today().year, '0%s' %datetime.date.today().isocalendar()[1] if datetime.date.today().isocalendar()[1] <10 else datetime.date.today().isocalendar()[1])
    # period_month = '%s-%s' %(datetime.date.today().year, '0%s' %datetime.date.today().month if datetime.date.today().month < 10 else datetime.date.today().month)
    # period_year = '%s' %datetime.date.today().year
    # period_dayfrom = period_day
    # period_dayto = period_day

    # print(datetime.date.today().year, datetime.date.today().isocalendar()[1])
    # print(request.POST)

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

    # print(histInfo)



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
    # listings_list_all_hist = []
    listings_list_all = []
    county_chart_all_hist = []
    county_chart_all = []
    print("there",connection.queries)
    for idx, hist in enumerate(histInfo):
        county_chart = []
        listings_list = []
        # listings_list_all_hist.append([])

        # ____________________ make initial QS ________________________

        # print(hist["property_type"])
        if hist["property_type"] == 'Sold':
            listings_qs = Listings.objects.filter(isactive__exact=False).filter(**filter_isnull_f).order_by(
                field)
        elif hist["property_type"] == 'Listings':
            listings_qs = Listings.objects.filter(**filter_isnull_f).order_by(field)
            #listings_qs = Listings.objects#.filter(latestprice__isnull = False)  # .order_by(field)
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
            dateto = datetime.datetime.strptime(hist["period_year"] + '-12-31',
                                                "%Y-%m-%d") + datetime.timedelta(days=1)
        else:  # Period
            datefrom = hist["period_dayfrom"]
            dateto = datetime.datetime.strptime(hist["period_dayto"], '%Y-%m-%d') + datetime.timedelta(days=1)

        if hist["property_type"] == 'Sold':
            listings_qs = listings_qs.filter(datesold__range=(datefrom, dateto))

        if hist["property_type"] == 'Listings':
            # listings_qs = listings_qs.annotate(di=Coalesce('dateinactive', datetime.date.today())) \
            #     .filter(datepublished__lt=dateto, di__gte=datefrom)
            listings_qs = listings_qs.annotate(di=Case(
                When(Q(dateinactive__isnull=False), then='dateinactive'),
                default=Value(datetime.date.today()),
                output_field=DateTimeField()
            )).filter(datepublished__lt=dateto, di__gte=datefrom)

        if (listings_qs.count()) == 0:
            messages.error(request, "No data for selected settings")
            break

        # _____________________ Generate ordered list of all results _______________
        # print(hist["county_selected"])
        print("here", connection.queries)

        for idy, county in enumerate(hist["county_selected"]):
            # print(idy, county)
            if county == 'Whole Sweden':
                # print(listings_qs.values(field))
                if hist_type == 'Price m2':
                    # for v in listings_qs.values('latestprice', 'livingarea'):
                    # print(v['latestprice'], v['livingarea'])
                    # print(v['latestprice'] / v['livingarea'])

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

    #print(connection.queries)
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
        # print(listings_list)
        hist = numpy.histogram(listings_list, bins=bins)
        listings_hist[0].append('%s' % county)
        tot = len(listings_list)

        listings_hist[1].append(len([n for n in listings_list if n < percentL_price]) / (tot if rel else 1))
        # print(hist)

        for i, h in enumerate(hist[0]):
            listings_hist[i + 2].append(h / (tot if rel else 1))

        listings_hist[-1].append(len([n for n in listings_list if n > percentH_price]) / (tot if rel else 1))

    # print(county_selected)
    # print(listings_hist)
    #print(connection.queries)
    context = {"histInfo": histInfo,
               "defHistInfo": defHistInfo,
               "county_list": county_list,
               "hist_type": hist_type,
               "chart_type": chart_type,
               "data_type": data_type[0],
               "listings_hist": listings_hist,
               "x_axis_title": x_axis_title,
               # "county_selected": county_selected,
               "num_bins": num_bins,
               "LowerCutoff": LowerCutoff,
               "UpperCutoff": UpperCutoff,
               "g_child": g_child,
               # "period_type" : period_type,
               # "period_day" : period_day,
               # "period_week" : period_week,
               # "period_month" : period_month,
               # "period_year" : period_year,
               # "period_dayfrom" : period_dayfrom,
               # "period_dayto" : period_dayto,

               }

    return render(request, "svrea/plots_histograms.html", context=context)



