import datetime

from ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.db.models import Func
from django.shortcuts import render, redirect, get_object_or_404
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

    #print(request)
    # if request.POST.get('change_posts'):


    posts = Posts.objects.order_by('-dateofcreation')
    # print('Permissions')
    # print(Permission.objects.filter(user=request.user))

    context = {"posts" : posts}
    return render(request, "posts/posts.html", context=context)


@login_required(login_url="/")
@permission_required('posts.add_posts', login_url='/')
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

    #print(request.POST)
    if request.POST.get('newpost'):
        title = request.POST.get('post_title')
        text = request.POST.get('post_text')
        post = Posts(
                dateofcreation=datetime.datetime.now(),
                createdby=request.user.username if request.user.is_authenticated() else '',
                title= title,
                text=text
            )
        post.save()
        messages.info(request, 'New post has been created.</br> You can see it <a href="%s">here</a>' %reverse("posts:details", kwargs={"id": post.id}))

    context = {"posts": posts}
    return render(request, "posts/new.html", context=context)


def details(request, id = None):
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

    post = get_object_or_404(Posts, id=id)

    context = {"post": post}
    return render(request, "posts/details.html", context=context)

@permission_required('posts.change_posts', login_url='/')
def edit(request, id = None):
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

    post = get_object_or_404(Posts, id=id)

    if request.POST.get('editpost'):
        title = request.POST.get('post_title')
        text = request.POST.get('post_text')
        post.title = title
        post.text = text
        post.save()
        messages.info(request, 'Post has been updated.</br> You can see it <a href="%s">here</a>' %reverse("posts:details", kwargs={"id": post.id}))

    context = {"post": post}
    return render(request, "posts/edit.html", context=context)


@permission_required('posts.delete_posts', login_url='/')
def delete(request, id = None):
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

    post = get_object_or_404(Posts, id=id)
    post.delete()

    messages.info(request, 'Post has been deleted')
    return redirect('posts:posts')