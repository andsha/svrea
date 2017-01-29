from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout


@login_required(redirect_field_name = "", login_url="/")
@permission_required('svrea_script.can_run_script')
def script_run(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect("index")



    context = {
        "text" : "You can run scrip"
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