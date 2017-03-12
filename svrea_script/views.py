import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib import messages

from script.svrea_script import Svrea_script
from svrea_script.models import Info, Aux, Log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rq import Queue
from worker import conn


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_run_script')
def script_run(request):

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
        else:
            messages.error(request, "neither upload nor download was found in config")

        if aux is not None:
            aux.value='stopped'
            aux.save()
            info.status = 'stopped'
            info.save()

    # if request.POST.get('download'):
    #
    #     #params = {1:2, 3:4}
    #     #script = Svrea_script(params=params, username=request.user.username)
    #     #res = q.enqueue(script.run)

    if request.POST.get('download'):
        q = Queue(connection=conn)
        params = {'download': request.POST.get('download'),
                  'forced' : True if request.POST.get('forced') is not None else False,
                  'downloadLast' : True if request.POST.get('downloadLast') else False}
        script = Svrea_script(params=params, username=request.user.username)
        res = q.enqueue(script.run)


    if request.POST.get('upload'):
        q = Queue(connection=conn)
        params = {'upload' : True,
                  'forced' : True}
        script = Svrea_script(params=params, username=request.user.username)
        res = q.enqueue(script.run)

    running_scripts = Info.objects.all().filter(status__exact = 'started')

    context = {
        "text" : '',
        "running_scripts" : running_scripts
    }
    time.sleep(.1)
    return render(request, "svrea_script/run.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_see_history')
def script_history(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    history = Info.objects.all().order_by('started')

    context = {
        "text" : "You can see script history",
        "history" : history
    }
    return render(request, "svrea_script/history.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_see_script_logs')
def script_logs(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    alllogs = Log.objects.order_by('-when')
    paginator = Paginator(alllogs, 20, orphans=9)
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