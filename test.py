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




SELECT DISTINCT ON ("svrea_script_address"."county") "svrea_script_address"."addressid", "svrea_script_address"."house", "svrea_script_address"."street", "svrea_script_address"."city", "svrea_script_address"."municipality", "svrea_script_address"."county", "svrea_script_address"."areaname", "svrea_script_address"."country" FROM "svrea_script_address" INNER JOIN "svrea_script_listings" ON ("svrea_script_address"."addressid" = "svrea_script_listings"."address_id") WHERE "svrea_script_listings"."isactive" = true ORDER BY "svrea_script_address"."county" ASC', 'time': '0.336'

SELECT "svrea_script_listings"."booliid",
        "svrea_script_listings"."datepublished",
        "svrea_script_listings"."source_id",
        "svrea_script_listings"."address_id",
        "svrea_script_listings"."latitude",
        "svrea_script_listings"."longitude",
        "svrea_script_listings"."constructionyear",
        "svrea_script_listings"."rent",
        "svrea_script_listings"."url",
        "svrea_script_listings"."rooms",
        "svrea_script_listings"."propertytype",
        "svrea_script_listings"."plotarea",
        "svrea_script_listings"."additionalarea",
        "svrea_script_listings"."livingarea",
        "svrea_script_listings"."floor",
        "svrea_script_listings"."isnewconstruction",
        "svrea_script_listings"."datesold",
        "svrea_script_listings"."isactive",
        "svrea_script_listings"."dateinactive",
        "svrea_script_listings"."latestprice",
        COALESCE("svrea_script_listings"."dateinactive", '2017-07-08'::date) AS "di"
FROM "svrea_script_listings"
WHERE ("svrea_script_listings"."latestprice" IS NOT NULL AND
        "svrea_script_listings"."datepublished" < '2017-07-08T00:00:00'::timestamp AND
        COALESCE("svrea_script_listings"."dateinactive", '2017-07-08'::date) >= '2017-07-07T00:00:00'::timestamp)
ORDER BY "svrea_script_listings"."latestprice" ASC

SELECT "svrea_script_listings"."latestprice"
FROM "svrea_script_listings"
WHERE ("svrea_script_listings"."latestprice" IS NOT NULL AND
        "svrea_script_listings"."datepublished" < '2017-07-08T00:00:00'::timestamp AND
        COALESCE("svrea_script_listings"."dateinactive", '2017-07-08'::date) >= '2017-07-07T00:00:00'::timestamp)
ORDER BY "svrea_script_listings"."latestprice" ASC

SELECT "svrea_script_listings"."booliid", "svrea_script_listings"."datepublished", "svrea_script_listings"."source_id", "svrea_script_listings"."address_id", "svrea_script_listings"."latitude", "svrea_script_listings"."longitude", "svrea_script_listings"."constructionyear", "svrea_script_listings"."rent", "svrea_script_listings"."url", "svrea_script_listings"."rooms", "svrea_script_listings"."propertytype", "svrea_script_listings"."plotarea", "svrea_script_listings"."additionalarea", "svrea_script_listings"."livingarea", "svrea_script_listings"."floor", "svrea_script_listings"."isnewconstruction", "svrea_script_listings"."datesold", "svrea_script_listings"."isactive", "svrea_script_listings"."dateinactive", "svrea_script_listings"."latestprice", COALESCE("svrea_script_listings"."dateinactive", \'2017-07-08\'::date) AS "di" FROM "svrea_script_listings" WHERE ("svrea_script_listings"."latestprice" IS NOT NULL AND "svrea_script_listings"."datepublished" < \'2017-07-08T00:00:00\'::timestamp AND COALESCE("svrea_script_listings"."dateinactive", \'2017-07-08\'::date) >= \'2017-07-07T00:00:00\'::timestamp) ORDER BY "svrea_script_listings"."latestprice" ASC



select
c.type,
case when c.type='monucipality' then municipality
        when c.type='city' then ciy
        default county
end as geogpr_name,
count(*)
FROM
etl_listings
join
(
SELECT
        'municipality' as type
UNION
SELECT
        'city' as type
UNION
SELECT
        'county' as type
) c on 1=1


