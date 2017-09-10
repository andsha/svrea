import time
import datetime
from rq import Queue
from worker import conn

from globalvars import workertimeout

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.db.models import Func
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from django.template.loader import render_to_string



from script.svrea_script import Svrea_script, area_list
from svrea_script.models import Info, Aux, Log, Rawdata
from svrea_etl.models import EtlListingsMonthly, EtlListingsQuarterly, EtlListingsYearly
from posts.models import Posts

class Len_Of_JSON_Field(Func):
    # function = 'length'
    # template = "%(function)s(%(expressions)s::text)"
    # select
    template = "jsonb_array_length(COALESCE(%(expressions)s->'sold', %(expressions)s->'listings') )"

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

class To_char(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(dtype)s')"

@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_run_script')
def script_run(request):
    #print(request.POST)
    # return 0
    if request.POST.get('runsql'):
        sqlquery = request.POST.get('sqlquery')
        sqlres = request.POST.get('sqlres')
    else:
        sqlquery = 'SQL Query'
        sqlres = 'SQL result'

    etlperiodtype = 'Daily'

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")
    elif request.POST.get('stopScript'):
        id = request.POST.get('stopScript').split('_')[1]
        info = Info.objects.get(id = id)
        aux = None

        if 'upload' in info.config:
            aux = Aux.objects.get(key='UploadAuxKey')
        elif 'download' in info.config:
            aux = Aux.objects.get(key='DownloadAuxKey')
        elif 'analyze' in info.config:
            aux = Aux.objects.get(key='AnalyzeAuxKey')
        else:
            messages.error(request, "Action is not one of those: Upload, Download, Analyze")

        if aux is not None:
            aux.value='stopped'
            aux.save()
            info.status = 'stopped'
            info.save()
    elif request.POST.get('download'):
        q = Queue(connection=conn)
        params = {'download': request.POST.get('download'),
                  'forced' : True if request.POST.get('forced') is not None else False,
                  'downloadLast' : True if request.POST.get('downloadLast') else False,
                  'area' : request.POST.getlist('area')
                  }
        script = Svrea_script(params=params, username=request.user.username)
        res = q.enqueue(script.run, timeout=workertimeout)
    elif request.POST.get('upload'):
        q = Queue(connection=conn)
        params = {'upload' : True,
                  'forced' : True}
        script = Svrea_script(params=params, username=request.user.username)
        res = q.enqueue(script.run, timeout=workertimeout)
    elif request.POST.get('analyze'):
        q = Queue(connection=conn)
        etlperiodtype = request.POST.get('etlperiodtype')
        numThreads = request.POST.get('numThreads')
        params = {'analyze' : True,
                  'forced' : True,
                  'etlRange' : "%s:%s" %(request.POST.get('etlFromDate'), request.POST.get('etlToDate')),
                  'etlPeriodType' : etlperiodtype,
                  'numThreads' : numThreads
                  }
        script = Svrea_script(params=params, username=request.user.username)

        res = q.enqueue(script.run, timeout=workertimeout)
    elif request.POST.get('runsql'):
        sql = request.POST.get('sqlquery')
        #print(sql)
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                sqlres = [[str(s) for s in row] for row in cursor.fetchall()]
            except Exception as e:
                sqlres = e
    elif request.POST.get("newpost"):
        blogperiodtype = request.POST.get('blogperiodtype')
        blogperiod = datetime.datetime.strptime(request.POST.get('blogperiod'), '%Y-%m-%d')

        if blogperiodtype == 'Monthly':
            blogperiod = blogperiod.replace(day = 1)
            previous_period1 = blogperiod.replace(month = blogperiod.month - 1)
            previous_period2 = blogperiod.replace(year = blogperiod.year - 1)
            previous_period3 = blogperiod.replace(year = blogperiod.year - 2)
            qs = EtlListingsMonthly.objects

        regions = ['Sweden', 'Uppsala', 'Göteborg', 'Malmö', 'Stockholm']
        regions.sort()
        data = qs.filter(
            record_firstdate__in = [blogperiod, previous_period1, previous_period2, previous_period3],
            geographic_name__in = regions,
            property_type = 'Lägenhet'
            ).annotate(date = To_char('record_firstdate', dtype = 'YYYY-MM-DD'))\
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
        rdata = {regions[i] : data[i::len(regions)] for i in range(len(regions))}

        # for r in rdata:
        #     print(r, rdata[r])

        for a in rdata:
            rdata[a][0]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][0]['active_listings'] -1)*100
            rdata[a][1]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][1]['active_listings'] - 1)*100
            rdata[a][2]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][2]['active_listings'] - 1)*100

            rdata[a][0]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][0]['sold_today'] - 1)*100
            rdata[a][1]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][1]['sold_today'] - 1)*100
            rdata[a][2]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][2]['sold_today'] - 1)*100

            rdata[a][0]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][0]['sold_price_med'] - 1)*100
            rdata[a][1]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][1]['sold_price_med'] - 1)*100
            rdata[a][2]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][2]['sold_price_med'] - 1)*100

            rdata[a][0]['sold_price_sqm_med'] = (rdata[a][3]['sold_price_sqm_med'] / rdata[a][0]['sold_price_sqm_med'] - 1)*100
            rdata[a][1]['sold_price_sqm_med'] = (rdata[a][3]['sold_price_sqm_med'] / rdata[a][1]['sold_price_sqm_med'] - 1)*100
            rdata[a][2]['sold_price_sqm_med'] = (rdata[a][3]['sold_price_sqm_med'] / rdata[a][2]['sold_price_sqm_med'] - 1)*100

            rdata[a][0]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][0]['sold_area_med'] - 1)*100
            rdata[a][1]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][1]['sold_area_med'] - 1)*100
            rdata[a][2]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][2]['sold_area_med'] - 1)*100

        # for d in rdata:
        #     print(d)

        post = Posts(
            dateofcreation=datetime.datetime.now(),
            createdby=request.user.username if request.user.is_authenticated() else '',
            source='',
            title='Monthly statistics for %s %s' %(blogperiod.strftime('%B'), blogperiod.strftime('%Y')),
            text=''
        )
        post.save()

        context = {
            "idnum": post.id,
            "Sweden" : rdata['Sweden'],
            "Uppsala": rdata['Uppsala'],
            "Göteborg": rdata['Göteborg'],
            "Malmö": rdata['Malmö'],
            "Stockholm": rdata['Stockholm']
        }

        text = render_to_string('posts/post_template.html', context=context)
        post.text = text
        post.save()





    running_scripts = Info.objects.all().filter(status__exact = 'started')

    context = {
        "text" : '',
        "running_scripts" : running_scripts,
        "area_list" : area_list,
        "etlperiodtype" : etlperiodtype,
        "sqlquery" : sqlquery,
        "sqlres" : sqlres
    }
    time.sleep(.1)
    return render(request, "svrea_script/run.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_see_info')
def script_info(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    if request.POST.get('deleteInfo'):
        infoid = request.POST.get('deleteInfo').split('_')[1]
        num = Info.objects.get(id = infoid).delete()

    info = Info.objects.all().order_by('-started')
    paginator = Paginator(info, 50, orphans=9)
    page = request.GET.get('page')

    try:
        info = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        info = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        info = paginator.page(paginator.num_pages)

    context = {
        "info" : info
    }
    return render(request, "svrea_script/info.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_see_script_logs')
def script_logs(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    alllogs = Log.objects.order_by('-when')
    paginator = Paginator(alllogs, 50, orphans=9)
    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        logs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        logs = paginator.page(paginator.num_pages)

    context = {
        "logs" : logs
    }
    return render(request, "svrea_script/logs.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_see_data')
def script_data(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    #info = Rawdata.objects.annotate(sizeofdata=Len_Of_JSON_Field('rawdata')).order_by('downloaded').all()
    alldata = Rawdata.objects.order_by('-downloaded').defer('rawdata')
    paginator = Paginator(alldata, 100, orphans=9)
    page = request.GET.get('page')
    try:
        alldata = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        alldata = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        alldata = paginator.page(paginator.num_pages)

    context = {
        "alldata" : alldata
    }
    return render(request, "svrea_script/data.html", context=context)