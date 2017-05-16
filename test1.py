def testfunc():
    print('hello')
    return 5



select count(*) from svrea_script_listings l join svrea_script_address a on l.address_id = a.addressid where a.municipality='Stockholm' and datesold::date='2017-05-14'