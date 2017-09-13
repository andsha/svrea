
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, reverse, redirect
# Create your views here.

def index(request):
    return redirect(reverse('tables:summary'))

def summary(request):
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

    context = {}
    return render(request, "tables/summary.html", context=context)

#
# blogperiodtype = request.POST.get('blogperiodtype')
# blogperiod = datetime.datetime.strptime(request.POST.get('blogperiod'), '%Y-%m-%d')
#
# if blogperiodtype == 'Monthly':
#     blogperiod = blogperiod.replace(day=1)
#     previous_period1 = blogperiod.replace(month=blogperiod.month - 1)
#     previous_period2 = blogperiod.replace(year=blogperiod.year - 1)
#     previous_period3 = blogperiod.replace(year=blogperiod.year - 2)
#     qs = EtlListingsMonthly.objects
#
# etlperiod = blogperiodtype
# etldate = blogperiod
#
# regions = ['Sweden', 'Uppsala', 'Göteborg', 'Malmö', 'Stockholm']
# regions.sort()
# data = qs.filter(
#     record_firstdate__in=[blogperiod, previous_period1, previous_period2, previous_period3],
#     geographic_name__in=regions,
#     property_type='Lägenhet'
# ).annotate(date=To_char('record_firstdate', dtype='YYYY-MM-DD')) \
#     .values(
#     'date',
#     'geographic_name',
#     'active_listings',
#     'sold_today',
#     'sold_price_med',
#     'sold_price_sqm_med',
#     'sold_area_med'
# ).order_by('record_firstdate', 'geographic_name')
#
# # for r in data:
# #     print (r)
# rdata = {regions[i]: data[i::len(regions)] for i in range(len(regions))}
#
# # for r in rdata:
# #     print(r, rdata[r])
#
# for a in rdata:
#     rdata[a][0]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][0]['active_listings'] - 1) * 100
#     rdata[a][1]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][1]['active_listings'] - 1) * 100
#     rdata[a][2]['active_listings'] = (rdata[a][3]['active_listings'] / rdata[a][2]['active_listings'] - 1) * 100
#
#     rdata[a][0]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][0]['sold_today'] - 1) * 100
#     rdata[a][1]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][1]['sold_today'] - 1) * 100
#     rdata[a][2]['sold_today'] = (rdata[a][3]['sold_today'] / rdata[a][2]['sold_today'] - 1) * 100
#
#     rdata[a][0]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][0]['sold_price_med'] - 1) * 100
#     rdata[a][1]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][1]['sold_price_med'] - 1) * 100
#     rdata[a][2]['sold_price_med'] = (rdata[a][3]['sold_price_med'] / rdata[a][2]['sold_price_med'] - 1) * 100
#
#     rdata[a][0]['sold_price_sqm_med'] = (
#                                         rdata[a][3]['sold_price_sqm_med'] / rdata[a][0]['sold_price_sqm_med'] - 1) * 100
#     rdata[a][1]['sold_price_sqm_med'] = (
#                                         rdata[a][3]['sold_price_sqm_med'] / rdata[a][1]['sold_price_sqm_med'] - 1) * 100
#     rdata[a][2]['sold_price_sqm_med'] = (
#                                         rdata[a][3]['sold_price_sqm_med'] / rdata[a][2]['sold_price_sqm_med'] - 1) * 100
#
#     rdata[a][0]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][0]['sold_area_med'] - 1) * 100
#     rdata[a][1]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][1]['sold_area_med'] - 1) * 100
#     rdata[a][2]['sold_area_med'] = (rdata[a][3]['sold_area_med'] / rdata[a][2]['sold_area_med'] - 1) * 100
#
# # for d in rdata:
# #     print(d)
#
# post = Posts(
#     dateofcreation=datetime.datetime.now(),
#     createdby=request.user.username if request.user.is_authenticated() else '',
#     source='',
#     etlperiod=etlperiod,
#     etldate=etldate,
#     title='Monthly statistics for %s %s' % (blogperiod.strftime('%B'), blogperiod.strftime('%Y')),
#     text=''
# )
# post.save()
#
# context = {
#     "idnum": post.id,
#     "Sweden": rdata['Sweden'],
#     "Uppsala": rdata['Uppsala'],
#     "Göteborg": rdata['Göteborg'],
#     "Malmö": rdata['Malmö'],
#     "Stockholm": rdata['Stockholm']
# }
#
# text = render_to_string('posts/post_template.html', context=context)
# post.text = text
# post.save()