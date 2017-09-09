
from ratelimit.decorators import ratelimit

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .models import Posts



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