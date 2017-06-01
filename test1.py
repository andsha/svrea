def testfunc():
    print('hello')
    return 5



select count(*) from svrea_script_listings l join svrea_script_address a on l.address_id = a.addressid where a.municipality='Stockholm' and datesold::date='2017-05-14'
select sum(l.latestprice)/count(*)  from svrea_script_listings l join svrea_script_address a on l.address_id = a.addressid where l.datesold='2017-05-26' and a.county='Skåne län';