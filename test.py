import time

import redis
from rq import Queue

from static.maps.Sweden.Reduce_polygons import testfunc

#redis_conn = Redis(port=6379)
#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_conn = redis.from_url('redis://localhost:6379')
q = Queue(connection = redis_conn)

res = q.enqueue(testfunc)

print (res.result)

time.sleep(5)

print(res.result)





select
count(*)
from
listings
join adresses
where l.floor=1
group by 1



having min(l.floor)=1

listing = Listings.objects.annotate(whatever='address__county' if gtype == 'county' else 'address__municipality') \
    .values('whatever') \
    .filter(isactive__exact=True) \
    .annotate(listing_counts=Count('booliid'))



listing = Listings.objects.values('address__county' if 'county' == 'county' else 'address__municipality') \
    .filter(isactive__exact=True) \
    .annotate(listing_counts=Count('booliid'))



select record_date, geographic_name, active_listings, listing_price_med, active_listings, listing_area_avg from svrea_etl_etllistings where record_date = '2017-02-04'  and (active_listings is NULL or listing_price_med is NULL or active_listings is NULL or listing_area_avg is NULL);
select count(*) from svrea_script_listings l join svrea_script_address a on l.address_id=a.addressid where a.municipality='Habo' and l.datepublished<='2017-02-04' and (l.dateinactive >'2017-02-04' or l.dateinactive is NULL);

select livingarea from svrea_script_listings l join svrea_script_address a on l.address_id=a.addressid where a.municipality='Habo' and l.datepublished<='2017-02-04' and (l.dateinactive >'2017-02-04' or l.dateinactive is NULL);
