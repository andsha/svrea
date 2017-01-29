from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):

    if request.POST.get('submit') == 'Log Out':
        logout(request)
        return redirect('index')

    if request.POST.get('submit') == 'Log In':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Please Enter Correct User Name and Password ")
            return redirect('index')

    if request.user.is_authenticated:
        return index_login(request)
    else:
        return index_nologin(request)


def index_nologin(request):
    context = {}
    return render(request, "svrea/index_nologin.html", context=context)



def index_login(request):
    context = {}
    return render(request, "svrea/index_login.html", context=context)




@login_required(redirect_field_name = "", login_url="/")

def listings_map(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)

    context = {
        "success": False
    }
    return render(request, "svrea/index_login.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
def density_map(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)

    context = {
        "success": False
    }
    return render(request, "svrea/index_login.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
def price_density_map(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)

    context = {
        "success": False
    }
    return render(request, "svrea/index_login.html", context=context)


@login_required(redirect_field_name = "", login_url="/")
def plots_histograms(request):
    if request.POST.get('submit') == 'Log Out':
        logout(request)

    context = {
        "success": False
    }
    return render(request, "svrea/index_login.html", context=context)



