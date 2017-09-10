import datetime
from ratelimit.decorators import ratelimit

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

def newpost(request):
    ts_data = [['haxis', 'available listings']]

    data = EtlListingsDaily.objects.filter(
        record_firstdate__range = (datetime.date(year=2017, month=1, day=1), datetime.date(year=2017, month=9, day=1)),
        geographic_name = 'Sweden'
    ).annotate(date = To_char('record_firstdate', dtype = 'YYYY-MM-DD')).values('date','active_listings').order_by('record_firstdate')

    for d in data:
        ts_data.append([d['date'],d['active_listings']])

    post = Posts(
        dateofcreation = datetime.datetime.now(),
        createdby = request.user.username if request.user.is_authenticated() else '',
        source = '',
        title = 'This is a test post',
        text = ''
    )
    post.save()

    context = {
        "idnum" : post.id,
        "ts_data": ts_data,
        "x_axis_title": "Date",
        "y_axis_title": "Number of Properties",
        "chart_type": "Line"
    }

    text = render_to_string('posts/post_template.html', context=context)
    post.text = text
    post.save()

    return posts(request)
