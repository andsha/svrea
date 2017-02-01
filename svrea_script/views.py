from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout

from script.svrea_script import svrea_script


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_run_script')
def script_run(request):

    text = 'nothing'
    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")

    if request.POST.get('run_script') == '':
        text = request.POST.get('script_params')
        script = svrea_script()
        script.run(text)




    context = {
        "text" : text
    }
    return render(request, "svrea_script/run.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_see_history')
def script_history(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")



    context = {
        "text" : "You can see script history"
    }
    return render(request, "svrea_script/history.html", context=context)