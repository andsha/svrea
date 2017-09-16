from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Func
from django.shortcuts import render, reverse, redirect

from svrea_etl.models import EtlListingsMonthly, EtlListingsQuarterly, EtlListingsYearly


import calendar
import datetime


def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, calendar.monthrange(y, m)[1])
    return date.replace(day=d,month=m, year=y)

class To_char(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(dtype)s')"


def index(request):
    return redirect(reverse('tables:summary'))

def summary(request):
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

    period_type = 'Monthly'
    period = datetime.date.today().replace(day=1)
    month = '%s %s' %(calendar.month_name[datetime.date.today().month], datetime.date.today().year)
    quarter = 'Q%s %s' %(1 if datetime.date.today().month <= 3
                         else 2 if datetime.date.today().month <= 6
                         else 3 if datetime.date.today().month <= 9
                         else 4, datetime.date.today().year)
    year = datetime.date.today().year
    caption = "Numbers in the table refer to: Current Value/Change from Last Month/Change from Last Year/Change from 3 Years before"

    if request.GET.get('period_type'):
        period_type = request.GET.get('period_type')

        if period_type == 'Monthly':
            pms, pys = request.GET.get('month').split()
            #print({name: num for num, name in enumerate(calendar.month_name) if num})
            period = datetime.date(day = 1,
                                   month={name: num for num, name in enumerate(calendar.month_name) if num}[pms.strip()],
                                   year=int(pys))
            month = request.GET.get('month')

        elif period_type == 'Quarterly':
            pms, pys = request.GET.get('quarter').split()
            period = datetime.date(day = 1,
                                   month={
                                       "Q1" : 1,
                                       "Q2" : 4,
                                       "Q3" : 7,
                                       "Q4" : 10,
                                   }[pms],
                                   year=int(pys))
            quarter = request.GET.get('quarter')

        elif period_type == 'Yearly':
            period = datetime.date(day = 1,
                                   month = 1,
                                   year = int(request.GET.get('year')))
            year = request.GET.get('year')

    if period_type == 'Monthly':
        previous_period1 = monthdelta(period,-1)
        previous_period2 = period.replace(year=period.year - 1)
        previous_period3 = period.replace(year=period.year - 3)
        qs = EtlListingsMonthly.objects

    if period_type == 'Quarterly':
        previous_period1 = monthdelta(period,-4)
        previous_period2 = period.replace(year=period.year - 1)
        previous_period3 = period.replace(year=period.year - 3)
        qs = EtlListingsQuarterly.objects

    if period_type == 'Yearly':
        previous_period1 = period.replace(year=period.year - 1)
        previous_period2 = period.replace(year=period.year - 2)
        previous_period3 = period.replace(year=period.year - 3)
        qs = EtlListingsYearly.objects

    regions = ['Sweden', 'Uppsala', 'Göteborg', 'Malmö', 'Stockholm']
    regions.sort()

    data = qs.filter(
        record_firstdate__in=[period, previous_period1, previous_period2, previous_period3],
        geographic_name__in=regions,
        property_type='Lägenhet'
    ).annotate(date=To_char('record_firstdate', dtype='YYYY-MM-DD')) \
        .values(
        'date',
        'geographic_name',
        'active_listings',
        'sold_today',
        'sold_price_med',
        'sold_price_sqm_med',
        'sold_area_med'
    ).order_by('record_firstdate', 'geographic_name')

    # for r in data:
    #     print (r)
    rdata = {regions[i]: data[i::len(regions)] for i in range(len(regions))}

    # for r in rdata:
    #     print(r, rdata[r])

    for a in rdata:
        rdata[a][0]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][0]['active_listings'] - 1) * 100
        rdata[a][1]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][1]['active_listings'] - 1) * 100
        rdata[a][2]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][2]['active_listings'] - 1) * 100

        rdata[a][0]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][0]['sold_today'] - 1) * 100
        rdata[a][1]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][1]['sold_today'] - 1) * 100
        rdata[a][2]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][2]['sold_today'] - 1) * 100

        rdata[a][0]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][0]['sold_price_med'] - 1) * 100
        rdata[a][1]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][1]['sold_price_med'] - 1) * 100
        rdata[a][2]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][2]['sold_price_med'] - 1) * 100

        rdata[a][0]['sold_price_sqm_med'] = (
                                            rdata[a][3]['sold_price_sqm_med'] / rdata[a][0]['sold_price_sqm_med'] - 1) * 100
        rdata[a][1]['sold_price_sqm_med'] = (
                                            rdata[a][3]['sold_price_sqm_med'] / rdata[a][1]['sold_price_sqm_med'] - 1) * 100
        rdata[a][2]['sold_price_sqm_med'] = (
                                            rdata[a][3]['sold_price_sqm_med'] / rdata[a][2]['sold_price_sqm_med'] - 1) * 100

        rdata[a][0]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][0]['sold_area_med'] - 1) * 100
        rdata[a][1]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][1]['sold_area_med'] - 1) * 100
        rdata[a][2]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][2]['sold_area_med'] - 1) * 100

    months = []
    d = datetime.date(day = 1, month=1,year=2013)
    while d < datetime.date.today():
        months.append("%s %s" %(calendar.month_name[d.month], d.year))
        d = monthdelta(d, 1)

    quarters = []
    q = datetime.date(day=1, month=1, year=2013)
    while q < datetime.date.today():
        quarters.append("Q%s %s" % (1 if q.month <= 3
                         else 2 if q.month <= 6
                         else 3 if q.month <= 9
                         else 4, q.year))
        q = monthdelta(q, 4)

    years = [y for y in range(2013, datetime.date.today().year + 1)]


    context = {
        "caption" : caption,
        "months" : months,
        "month" : month,
        "quarters" : quarters,
        "quarter": quarter,
        "years" : years,
        "year" :year,
        "Sweden": rdata['Sweden'],
        "Uppsala": rdata['Uppsala'],
        "Göteborg": rdata['Göteborg'],
        "Malmö": rdata['Malmö'],
        "Stockholm": rdata['Stockholm']
    }


    return render(request, "tables/summary.html", context=context)