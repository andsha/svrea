import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib import messages

from script.svrea_script import Svrea_script, area_list
from svrea_script.models import Info, Aux, Log, Rawdata
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Func
from django.db.models.functions import Length

from rq import Queue
from worker import conn

from globalvars import workertimeout

class Len_Of_JSON_Field(Func):
    # function = 'length'
    # template = "%(function)s(%(expressions)s::text)"
    # select
    template = "jsonb_array_length(COALESCE(%(expressions)s->'sold', %(expressions)s->'listings') )"


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_run_script')
def script_run(request):
    #print(request.POST)
    # return 0
    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    if request.POST.get('stopScript'):
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

    if request.POST.get('download'):
        q = Queue(connection=conn)
        params = {'download': request.POST.get('download'),
                  'forced' : True if request.POST.get('forced') is not None else False,
                  'downloadLast' : True if request.POST.get('downloadLast') else False,
                  'area' : request.POST.getlist('area')
                  }
        script = Svrea_script(params=params, username=request.user.username)
        res = q.enqueue(script.run, timeout=workertimeout)


    if request.POST.get('upload'):
        q = Queue(connection=conn)
        params = {'upload' : True,
                  'forced' : True}
        script = Svrea_script(params=params, username=request.user.username)
        res = q.enqueue(script.run, timeout=workertimeout)

    if request.POST.get('analyze'):
        q = Queue(connection=conn)
        params = {'analyze' : True,
                  'forced' : True,
                  'etlRange' : "%s:%s" %(request.POST.get('etlFromDate'), request.POST.get('etlToDate'))
                  }
        script = Svrea_script(params=params, username=request.user.username)

        res = q.enqueue(script.run, timeout=workertimeout)

    running_scripts = Info.objects.all().filter(status__exact = 'started')

    context = {
        "text" : '',
        "running_scripts" : running_scripts,
        "area_list" : area_list
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
    alldata = Rawdata.objects.order_by('downloaded').defer('rawdata')
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