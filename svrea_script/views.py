from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib import messages

from script.svrea_script import Svrea_script
from svrea_script.models import Info, Aux, Log



@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_run_script')
def script_run(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    if request.POST.get('stopScript'):
        id = request.POST.get('stopScript').split('_')[1]
        info = Info.objects.get(id = id)

        if 'update' in info.config:
            aux = Aux.objects.get(key='UploadAuxKey')
        elif 'download' in info.config:
            aux = Aux.objects.get(key='DownloadAuxKey')
        else:
            return 0

        aux.value='stopped'
        aux.save()
        info.status = 'stopped'
        info.save()

    if request.POST.get('download'):
        params = {'download': request.POST.get('download'),
                  'forced' : True,
                  'downloadLast' : True if request.POST.get('downloadLast') else False}
        script = Svrea_script(params=params, username=request.user.username)
        if script.run() != 0:
            messages.error(request, "Error. For details see logs")

    if request.POST.get('upload'):
        params = {'upload' : True,
                  'forced' : True}
        script = Svrea_script(params=params, username=request.user.username)
        if script.run() != 0:
            messages.error(request, "Error. For details see logs")

    # if request.POST.get('run_script') == '':
    #     params = request.POST.get('script_params')
    #     # info = Info(user_name = request.user.username, config=params, status='started')
    #     # info.save()
    #     script = Svrea_script(params = params, username = request.user.username)



    running_scripts = Info.objects.all().filter(status__exact = 'started')

    context = {
        "text" : '',
        "running_scripts" : running_scripts
    }
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

    logs = Log.objects.order_by('-when')

    context = {
        "logs" : logs
    }
    return render(request, "svrea_script/logs.html", context=context)