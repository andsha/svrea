from django.shortcuts import render, redirect
from django.contrib.auth import logout

def details(request, name = None):

    if not request.user.is_authenticated or request.user.username != name:
        return redirect('index') # kick out

    if request.POST.get('submit') == 'Log Out':
        logout(request)
    return redirect('index')

