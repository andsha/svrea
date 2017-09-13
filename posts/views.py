import datetime

from ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Func
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from .models import Posts
from svrea_etl.models import EtlListingsDaily


class To_char(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(dtype)s')"


@ratelimit(key='ip', rate='1/s')
def posts(request):
    #return redirect('maps_listings')
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

    posts = Posts.objects.all()

    context = {"posts" : posts}
    return render(request, "posts/posts.html", context=context)


@login_required(login_url="/")
@permission_required('posts.can_make_new_posts', login_url='/')
def newpost(request):
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

    context = {"posts": posts}
    return render(request, "posts/new.html", context=context)