#!/usr/bin/env python3

import os,sys
from urllib.request import urlopen
from hashlib import sha1
import string
import json
import datetime
from dateutil.relativedelta import relativedelta
import random
import time
import re

from django.db.models import Func, Count, Q, F, Avg, Aggregate, When, Case, Min, Max, ExpressionWrapper, IntegerField, FloatField
from django.db.models.functions import Coalesce
from svrea_script.models import Info, Log, Rawdata, Aux, Listings, Source, Address, Pricehistory
from svrea_etl.models import EtlHistory, EtlListingsDaily, EtlListingsWeekly, EtlListingsMonthly, EtlListingsQuarterly, EtlListingsYearly
import logging

gCallerId = 'scr06as'
gUniqueKey = '3i0WnjAooYIHhgnyUKF597moNCYnt449kZbK3YAR'

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gDBStruct = BASE_FOLDER + '/script/DBStruct.cfg'
gDBFillRules = BASE_FOLDER + '/script/DBFillRules.cfg'

WARNING = 1101
ERROR = 1102
INFO = 1103

area_list = [
            ['2',  'Stockholm lan'],
            ['26', 'Sodermanlands lan'],
            ['253', 'Ostergotland lan'],
            ['153', 'Jönköpings län'],
            ['783', 'Kronobergs lan'],
            ['381', 'Kalmar län'],
            ['64', 'Skåne län'],
            ['160', 'Hallands län'],
            ['23', 'Västra Götalands län'],
            ['118',  'Uppsala'],
            ['645',  'Gotland'],
            ['145', 'Blekinge lan'],
            ['390', 'Värmlands län'],
            ['318', 'Örebro län'],
            ['315', 'Västmanlands län'],
            ['322', 'Dalarnas län'],
            ['581', 'Gävleborgs län'],
            ['250', 'Västernorrlands län'],
            ['456', 'Jämtlands län'],
            ['588', 'Västerbottens län'],
            ['802', 'Norrbottens län']
             ]
area_list.sort(key = lambda x: int(x[0]) )


class Datetime_to_date(Func):
    function = 'EXTRACT'
    template = '%(expressions)s::date'

class Extract_date(Func):
    function = 'EXTRACT'
    template = "%(function)s('%(dtype)s' from %(expressions)s)"

class Percentile(Aggregate):
    function = None
    name = "percentile"
    template = "%(function)s(%(percentiles)s) WITHIN GROUP (ORDER BY %(" \
               "expressions)s)"

    def __init__(self, expression, percentiles, continuous=True, **extra):
        if isinstance(percentiles, (list, tuple)):
            percentiles = "array%(percentiles)s" % {'percentiles': percentiles}
        if continuous:
            extra['function'] = 'PERCENTILE_CONT'
        else:
            extra['function'] = 'PERCENTILE_DISC'
        super().__init__(expression, percentiles=percentiles, **extra)


def tolog(level, str):
    if level == WARNING:
        l = 'WARNING'
    elif level == ERROR:
        l = 'ERROR'
    else:
        l = 'INFO'

    log = Log(level = l, entry = str)
    log.save()


class Svrea_script():

    def __init__(self, params = None, username = None):
        self.options = params#self.handleParams(params)
        self.forced = False

        if 'forced' in self.options:
             if self.options['forced']:
                self.forced = True
             self.options.pop('forced', None)

        self.username = username
        self.today = datetime.date.today()


    def run(self):
        logging.basicConfig(filename='/tmp/log',
                           filemode='a',
                           format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                           datefmt='%H:%M:%S',
                           level=logging.DEBUG)

        if self.options is None:
            tolog(ERROR, "no known parameters were found: %s" % self.options)
            return 1

        # db_from_env = dj_database_url.config()
        # db = DataBase(connection = pgUtil.pgProcess(database=db_from_env['NAME'],
        #                                             host=db_from_env['HOST'],
        #                                             user=db_from_env['USER'],
        #                                             port=db_from_env['PORT'],
        #                                             password=db_from_env['PASSWORD']), frules = gDBFillRules)

        today = datetime.date.today()
        today_scripts = Info.objects.filter(started__date = today)
        info = None
        runtoday = False
        err = 0
        a = None

        # looking for script matching current config
        # if no script matching current config is found, then generate new Info entry
        for s in today_scripts:
            if s.config == self.options:
                runtoday = True
                if s.status == 'done' and not self.forced: # if successfully run before by any user
                    st = 'already run for %s by %s' %(self.options, self.username)
                    tolog(INFO, st)
                    return 1
                else:
                    s.status = 'started' # if not run or previous error then restart
                    s.user_name = self.username  # current user name
                    s.save()
                    info = s
                    break

        # New entry since no script matching current config was found
        if not runtoday:
            l = Info(user_name = self.username,
                     config = self.options,
                     status = 'started')
            l.save()
            info = l

        # ___ First, download data from web ___
        if 'download' in self.options:
            tolog(INFO, ("Downloading %s" %self.options['download']))
            a, created = Aux.objects.update_or_create(key = 'DownloadAuxKey', defaults={"key" : "DownloadAuxKey",
                                                                                "value" : "run"})
            err += self.getDataFromWeb(info = info, latest = True if 'downloadLast' in self.options and self.options['downloadLast'] else False)

        # ___ Second, upload downloaded data from data table to Listings, Address etc ___
        if 'upload' in self.options and self.options['upload']:
            tolog(INFO, 'Uploading data')
            a, created = Aux.objects.update_or_create(key='UploadAuxKey', defaults={"key": "UploadAuxKey",
                                                                         "value": "run"})
            err += self.uploadData(info=info)

        # ___ Third, do ETL on uploaded data ___
        if 'analyze' in self.options and self.options['analyze']:
            tolog(INFO, 'Analyzing Data')
            a, created = Aux.objects.update_or_create(key='AnalyzeAuxKey', defaults={"key": "AnalyzeAuxKey",
                                                                         "value": "run"})
            err += self.analyzeData(info=info)
        # -----------------------------------------------------------------------------------

        if a is not None:
            a.value = 'stop'
            a.save()

        return err


    def getDataFromWeb(self, info = None, latest = False):
        #print('downloading')
        uniqueString = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        timestamp = str(int(time.time()))
        hashstr = sha1((gCallerId + timestamp + gUniqueKey + uniqueString).encode('utf-8')).hexdigest()
        urlBase = 'HTTP://api.booli.se//'

        if not (self.options['download'] == 'listings' or self.options['download'] == 'sold'):
            tolog(ERROR, ("Wrong type of download %s" %self.options['download']))
            info.status = 'error'
            info.save()
            return 1

        urlBase += '%s?' % self.options['download']
        # area_list = ['64',  # Skane
        #              '160', #Halland
        #              # '23', # vastra gotalands
        #              # '2',  # Stockholm lan
        #              # '783', # Kronobergs lan
        #              # '45', #Blekinge lan
        #              # '381', # Kalmar
        #              # '153', # Jonkoping
        #              # '253', # ostergotland lan
        #              # '26', # sodermanlands lan
        #              # '145', # Blekinge lan
        #              ]  #

        #tolog(INFO,latest)
        for idx, area in enumerate(self.options['area']):
            tolog(INFO, "Donwloading for area %s" % area)
            url = urlBase + \
                  'areaId=' + area + \
                  '&callerId=' + gCallerId + \
                  '&time=' + timestamp + \
                  '&unique=' + uniqueString + \
                  '&hash=' + str(hashstr)
            data = urlopen(url).read().decode('utf-8')
            dic = json.loads(data)
            maxcount = int(dic['totalCount'])

            if latest:
                maxcount = 300

            offset = 0
            limit = 300
            #offset = limit*225

            while 1:
                #tolog(INFO, "\n Beginning of cycle. offset=" + str(offset)+' limit='+str(limit))
                if Aux.objects.get(key = 'DownloadAuxKey').value != 'run':
                    info.status = 'stopped'
                    info.save()
                    tolog(ERROR, 'script %s %s was stopped by %s' %(info.id, info.config, self.username))
                    #print('stop thread')
                    return 1

                tolog(INFO, "%s out of %s" % (int(offset / limit) + 1, int(maxcount / limit)))
                uniqueString = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
                timestamp = str(int(time.time()))
                hashstr = sha1((gCallerId + timestamp + gUniqueKey + uniqueString).encode('utf-8')).hexdigest()
                url = urlBase + \
                      'areaId=' + area + \
                      '&offset=' + str(offset) + \
                      '&limit=' + str(limit) + \
                      '&callerId=' + gCallerId + \
                      '&time=' + timestamp + \
                      '&unique=' + uniqueString + \
                      '&hash=' + str(hashstr)

                #tolog(INFO,'trying to tetch url %s' %url)
                data = urlopen(url).read().decode('utf-8')
                #tolog(INFO,'fetch OK')
                dic = json.loads(data)
                raw_data = Rawdata(areacode=area,
                                   rawdata=dic,
                                   type=self.options['download'],
                                   downloaded=datetime.datetime.now())
                raw_data.save()
                #tolog(INFO,'data saved. waiting')
                offset += limit

                if offset >= maxcount:
                    tolog(INFO, "Downloading complete")
                    break
                if latest:
                    #print('latest only')
                    tolog(INFO, "Downloading complete")
                    break

                time.sleep(random.randint(15, 30))

            if idx < len(area_list) - 1:
                time.sleep(random.randint(15, 30))

        info.status = 'done'
        info.save()
        tolog(INFO, 'download completed')
        return 0


    def uploadData(self, info=None):
        data_to_upload = Rawdata.objects.filter(isuploaded__exact=False). \
            annotate(downloaded_date=Datetime_to_date('downloaded')). \
            order_by('downloaded_date', '-type', 'areacode')

        for data in data_to_upload:
            today = data.downloaded.date()
            if data.type == 'sold':
                Listings.objects.filter(isactive=True). \
                    update(isactive=False, dateinactive=today)
            # print(data.downloaded, data.uploaded, data.type, data.areacode)

            for listing in data.rawdata[data.type]:
                if Aux.objects.get(key='UploadAuxKey').value != 'run':
                    info.status = 'stopped'
                    info.save()
                    tolog(ERROR, 'script %s %s was stopped by %s' % (info.id, info.config, self.username))
                    return 1

                # *********************************************

                sourceid = listing['source']['id']
                sourcename = listing['source']['name']
                sourcetype = listing['source']['type']
                sourceurl = listing['source']['url']
                # print(sourceid, sourcename,sourcetype, sourceurl )

                (source, source_created) = Source.objects.update_or_create(
                    sourceid=sourceid,
                    defaults = {
                        'sourceid' : sourceid,
                        'name' : sourcename,
                        'sourcetype' : sourcetype,
                        'url' : sourceurl
                    }
                )

                #####################################################

                house = None
                street = None
                city = None
                county = None
                municipality = None
                areaname = None

                if 'streetAddress' in listing['location']['address']:
                    house = re.search('\\d+[^ ]*', listing['location']['address']['streetAddress'])

                    if house is not None:
                        house = house.group(0)
                    else:
                        house = None

                    street = re.sub('\\d+[^ ]*', '', listing['location']['address']['streetAddress'])

                if 'city' in listing['location']['address']:
                    city = listing['location']['address']['city']

                if 'region' in listing['location']:
                    if 'countyName' in listing['location']['region']:
                        county = listing['location']['region']['countyName']
                    if 'municipalityName' in listing['location']['region']:
                        municipality = listing['location']['region']['municipalityName']
                        if city is None:
                            city = municipality

                if 'namedAreas' in listing['location']:
                    areaname = listing['location']['namedAreas']

                address, address_created = Address.objects.update_or_create(
                    house=house,
                    street=street,
                    city=city,
                    municipality=municipality,
                    county=county,
                    defaults={
                        "areaname": areaname
                    }
                )

                #######################################################
                plotarea = None
                additionalarea = None
                livingarea = None
                floor = None
                isnewconstruction = False
                isactive = False
                datesold = None
                dateinactive = None
                latestprice = None
                rent = None
                constructionYear = None
                rooms = None
                soldprice = None
                listprice = None

                if 'rent' in listing:
                    rent = int(listing['rent'])
                if 'constructionYear' in listing:
                    constructionYear = listing['constructionYear']
                if 'rooms' in listing:
                    rooms = listing['rooms']
                if 'plotArea' in listing:
                    plotarea = listing['plotArea']
                if 'additionalArea' in listing:
                    additionalarea = listing['additionalArea']
                if 'livingArea' in listing:
                    livingarea = listing['livingArea']
                if 'floor' in listing:
                    floor = listing['floor']
                if 'isNewConstruction' in listing:
                    isnewconstruction = listing['isNewConstruction']
                if data.type == 'listings':
                    isactive = True
                    if 'listPrice' in listing:
                        listprice = int(listing['listPrice'])
                    latestprice = listprice
                if data.type == 'sold':
                    isactive = False
                    if 'soldPrice' in listing:
                        soldprice = int(listing['soldPrice'])
                    latestprice = soldprice
                    datesold = datetime.datetime.strptime(listing['soldDate'], '%Y-%m-%d')
                    dateinactive = datesold

                # print(listing['booliId'],
                #       listing['published'],
                #       listing['location']['position']['latitude'],
                #       listing['location']['position']['longitude'],
                #       constructionYear,
                #       rent,
                #       listing['url'],
                #       rooms,
                #       listing['objectType'],
                #       plotarea,
                #       additionalarea,
                #       livingarea,
                #       floor,
                #       isnewconstruction,
                #       datesold,
                #       isactive,
                #       latestprice,
                #       dateinactive)


                (listings, listings_created) = Listings.objects.update_or_create(
                    booliid=listing['booliId'],
                    defaults={
                        "datepublished": listing['published'] if 'published' in listing else None,
                        "source": source,
                        "address": address,
                        "latitude": listing['location']['position']['latitude'],
                        "longitude": listing['location']['position']['longitude'],
                        "constructionyear": constructionYear,
                        "rent": rent,
                        "url": listing['url'],
                        "rooms": rooms,
                        "propertytype": listing['objectType'],
                        "plotarea": plotarea,
                        "additionalarea": additionalarea,
                        "livingarea": livingarea,
                        "floor": floor,
                        "isnewconstruction": isnewconstruction,
                        "datesold": datesold,
                        "isactive": isactive,
                        "latestprice": latestprice,
                        "dateinactive": dateinactive
                    }
                )

                priceobj = Pricehistory.objects.filter(booliid=listing['booliId']).order_by('-date')

                newprice = latestprice
                newdate = today
                newissoldprice = False
                createnewprice = True

                if priceobj.count() > 0:
                    priceobj = priceobj[0]
                    if priceobj.issoldprice:  # last is sold
                        if data.type == 'sold':  # current is sold
                            if priceobj.date.date() == datesold.date():
                                if priceobj.price == latestprice:
                                    createnewprice = False
                                else:
                                    priceobj.date = datesold.date()
                                    priceobj.price = latestprice
                                    priceobj.save()
                                    createnewprice = False
                            else:
                                priceobj.date = datesold.date()
                                priceobj.price = latestprice
                                priceobj.save()
                                createnewprice = False
                    else:  # last is listing
                        if data.type == 'sold':  # current is sold
                            newissoldprice = True
                        else:  # current is listing
                            if latestprice == priceobj.price:
                                createnewprice = False
                else:
                    if data.type == 'sold':
                        newissoldprice = True

                if createnewprice:
                    newpriceobj = Pricehistory(
                        booliid=listings,
                        price=newprice,
                        date=newdate,
                        issoldprice=newissoldprice
                    )
                    newpriceobj.save()

            data.uploaded = datetime.datetime.now()
            data.isuploaded = True
            data.save()

        # aux = Aux.objects.get(key='UploadAuxKey')
        # aux.value = 'complete'
        # aux.save()

        info.status = 'done'
        info.save()

        return 0

    def analyzeData(self, info):
        stages = [
            'init',
            'check_tables',
            'fill_listings_daily_stats',
            'finish'
        ]
        startofperiod = datetime.datetime.strptime(self.options['etlRange'].split(':')[0], "%Y-%m-%d").date()
        endofperiod = datetime.datetime.strptime(self.options['etlRange'].split(':')[1], "%Y-%m-%d").date()

        if self.options['etlPeriodType'] == 'Weekly':
            # find monday of this week
            while startofperiod.weekday() != 0:
                startofperiod -= datetime.timedelta(days=1)
        elif self.options['etlPeriodType'] == 'Monthly':
            startofperiod = startofperiod.replace(day = 1)
        elif self.options['etlPeriodType'] == 'Quarterly':
            if startofperiod.month < 4:
                startofperiod = startofperiod.replace(day = 1, month = 1)
            elif startofperiod.month < 7:
                startofperiod = startofperiod.replace(day = 1, month = 3)
            elif startofperiod.month < 10:
                startofperiod = startofperiod.replace(day = 1, month = 6)
            elif startofperiod.month < 13:
                startofperiod = startofperiod.replace(day = 1, month = 9)
        elif self.options['etlPeriodType'] == 'Yearly':
            startofperiod = startofperiod.replace(day = 1, month = 1)

        dayFrom = startofperiod

        # loop through dates using etlPeriodType
        while dayFrom <= endofperiod:

            if Aux.objects.get(key='AnalyzeAuxKey').value != 'run':
                info.status = 'stopped'
                info.save()
                tolog(ERROR, 'script %s %s was stopped by %s' % (info.id, info.config, self.username))
                return 1

            #dayFrom = today
            dayTo = dayFrom

            if self.options['etlPeriodType'] == 'Daily':
                dayTo = dayFrom + datetime.timedelta(days=1)
            elif self.options['etlPeriodType'] == 'Weekly':
                dayTo = dayFrom + datetime.timedelta(days=7)
            elif self.options['etlPeriodType'] == 'Monthly':
                dayTo = dayFrom + relativedelta(months=1)
            elif self.options['etlPeriodType'] == 'Quarterly':
                dayTo = dayFrom + relativedelta(months=3)
            elif self.options['etlPeriodType'] == 'Yearly':
                dayTo = dayFrom + relativedelta(years=1)

            tolog(INFO, '%s analysis for %s' %(self.options['etlPeriodType'], dayFrom))
            for idx, stage in enumerate(stages):
                (hist, created) = EtlHistory.objects.get_or_create(
                    historydate__date = self.today,
                    etldate = dayFrom,
                    etlperiod = self.options['etlPeriodType'],
                    stage = stage,
                    defaults = {
                        'historydate'   : self.today,
                        'stage'         : stage,
                        'status'        : 'started'
                    }
                )

                if not created:
                    if hist.status == 'done' and not self.forced:
                        tolog(INFO, '%s Already run for %s' %(stage, dayFrom))
                        return 1
                    else:
                        hist.historydate = self.today
                        hist.status = 'started'
                        hist.save()

                if getattr(self, stage)(dayFrom, dayTo) == 0:  #use dayFrom and DayTo
                    hist.status = 'done'
                    hist.save()
                else:
                    hist.status = 'error'
                    hist.save()

            dayFrom = dayTo

            #today += datetime.timedelta(days=1) # use etlPeriodType as delta

        info.status = 'done'
        info.save()
        tolog(INFO, 'Analysis completed')
        return 0

#************************************************************************
    #Code for ETL stages
    def init(self, *args):
        return 0


    def check_tables(self, *args):
        return 0


    def fill_listings_daily_stats(self, dayFrom, dayTo):
        geographic_types = ['county', 'municipality', 'country']
        property_types = ['Villa', 'Lägenhet']
        #logging.info('bebebe')

        for gtype in geographic_types:
            for ptype in property_types:
                listing = Listings.objects.values('address__county' if gtype == 'county' else 'address__municipality' if gtype == 'municipality' else 'address__country')\
                    .filter(Q(datepublished__date__lt=dayTo) & (Q(dateinactive__isnull=True) | Q(dateinactive__date__gte=dayFrom))) \
                    .filter(propertytype = ptype)\
                    .annotate(listing_counts=Count('booliid'),
                              listing_price_avg = Avg('latestprice'),
                              listing_price_med = Percentile(expression='latestprice', percentiles=0.5),
                              # listing_price_85=Percentile(expression='latestprice', percentiles=0.85),
                              # listing_price_15=Percentile(expression='latestprice', percentiles=0.15),
                              listing_price_sqm_avg = Avg(F('latestprice') / Case(When(~Q(livingarea__exact = 0), then='livingarea'), default=None)),
                              listing_price_sqm_med = Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact = 0), then='livingarea'), default=None)), percentiles=.5),
                              #listing_price_sqm_15=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.15),
                              #listing_price_sqm_85=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.85),
                              listing_area_avg = Avg('livingarea'),
                              listing_area_med = Percentile(expression='livingarea', percentiles=.5),
                              #listing_area_15=Percentile(expression='livingarea', percentiles=.15),
                              #listing_area_85=Percentile(expression='livingarea', percentiles=.85),
                              listing_rent_avg=Avg('rent'),
                              listing_rent_med=Percentile(expression='rent', percentiles=.5),
                              #listing_rent_15=Percentile(expression='rent', percentiles=.15),
                              #listing_rent_85=Percentile(expression='rent', percentiles=.85),
                              )

                sold = Listings.objects.values('address__county' if gtype == 'county' else 'address__municipality' if gtype == 'municipality' else 'address__country') \
                    .filter(Q(datesold__date__lt = dayTo) & Q(datesold__date__gte = dayFrom)) \
                    .filter(propertytype=ptype) \
                    .annotate(sold_year = Extract_date('datesold', dtype = 'year'))\
                    .annotate(sold_counts=Count('booliid'),
                              sold_price_avg=Avg('latestprice'),
                              sold_price_med=Percentile(expression='latestprice', percentiles=0.5),
                              #sold_price_85=Percentile(expression='latestprice', percentiles=0.85),
                              #sold_price_15=Percentile(expression='latestprice', percentiles=0.15),
                              sold_price_sqm_avg=Avg(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),
                              sold_price_sqm_med=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.5),
                              #sold_price_sqm_15=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.15),
                              #sold_price_sqm_85=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.85),
                              sold_area_avg=Avg('livingarea'),
                              sold_area_med=Percentile(expression='livingarea', percentiles=.5),
                              #sold_area_15=Percentile(expression='livingarea', percentiles=.15),
                              #sold_area_85=Percentile(expression='livingarea', percentiles=.85),
                              sold_rent_avg=Avg('rent'),
                              sold_rent_med=Percentile(expression='rent', percentiles=.5),
                              #sold_rent_15=Percentile(expression='rent', percentiles=.15),
                              #sold_rent_85=Percentile(expression='rent', percentiles=.85),
                              sold_daysbeforesold_avg=Avg(F('datesold') - F('datepublished')),
                              sold_propertyage_avg = Avg(F('sold_year') - F('constructionyear'), output_field=FloatField())
                              )

                for l in listing:
                    etllistings = EtlListingsDaily.objects
                    if self.options['etlPeriodType'] == 'Weekly':
                        etllistings = EtlListingsWeekly.objects
                    elif self.options['etlPeriodType'] == 'Monthly':
                        etllistings = EtlListingsMonthly.objects
                    elif self.options['etlPeriodType'] == 'Quarterly':
                        etllistings = EtlListingsQuarterly.objects
                    elif self.options['etlPeriodType'] == 'Yearly':
                        etllistings = EtlListingsYearly.objects
                    (etllisting, created) = etllistings.update_or_create(
                        record_firstdate        = dayFrom,
                        geographic_type         = gtype,
                        geographic_name         = l['address__county' if gtype == 'county' else 'address__municipality' if gtype == 'municipality' else 'address__country'],
                        propertytype            = ptype,
                        defaults                = {
                            'active_listings'       : l['listing_counts'],
                            'listing_price_avg'     : l['listing_price_avg'],
                            'listing_price_med'     : l['listing_price_med'],
                            #'listing_price_85'      : l['listing_price_85'],
                            #'listing_price_15'      : l['listing_price_15'],
                            'listing_price_sqm_avg' : l['listing_price_sqm_avg'],
                            'listing_price_sqm_med' : l['listing_price_sqm_med'],
                            #'listing_price_sqm_15'  : l['listing_price_sqm_15'],
                            #'listing_price_sqm_85'  : l['listing_price_sqm_85'],
                            'listing_area_avg'      : l['listing_area_avg'],
                            'listing_area_med'      : l['listing_area_med'],
                            #'listing_area_15'       : l['listing_area_15'],
                            #'listing_area_85'       : l['listing_area_85'],
                            'listing_rent_avg'      : l['listing_rent_avg'],
                            'listing_rent_med'      : l['listing_rent_med'],
                            #'listing_rent_15'       : l['listing_rent_15'],
                            #'listing_rent_85'       : l['listing_rent_85'],
                        })

                    if self.options['etlPeriodType'] == 'Weekly':
                        etllisting.weekofyear = dayFrom.isocalendar()[1]
                    elif self.options['etlPeriodType'] == 'Monthly':
                        etllisting.monthofyear = dayFrom.month
                    elif self.options['etlPeriodType'] == 'Quarterly':
                        etllisting.quarterofyear = int((dayFrom.month - 1) / 3)  + 1
                    etllisting.save()

                for s in sold:
                    etlsolds = EtlListingsDaily.objects
                    if self.options['etlPeriodType'] == 'Weekly':
                        etlsolds = EtlListingsWeekly.objects
                    elif self.options['etlPeriodType'] == 'Monthly':
                        etlsolds = EtlListingsMonthly.objects
                    elif self.options['etlPeriodType'] == 'Quarterly':
                        etlsolds = EtlListingsQuarterly.objects
                    elif self.options['etlPeriodType'] == 'Yearly':
                        etlsolds = EtlListingsYearly.objects
                    (etlsold, created) = etlsolds.update_or_create(
                        record_firstdate=dayFrom,
                        geographic_type=gtype,
                        geographic_name=s['address__county' if gtype == 'county' else 'address__municipality' if gtype == 'municipality' else 'address__country'],
                        propertytype=ptype,
                        defaults={
                            'sold_today'            : s['sold_counts'],
                            'sold_price_avg'        : s['sold_price_avg'],
                            'sold_price_med'        : s['sold_price_med'],
                            #'sold_price_85'         : s['sold_price_85'],
                            #'sold_price_15'         : s['sold_price_15'],
                            'sold_price_sqm_avg'    : s['sold_price_sqm_avg'],
                            'sold_price_sqm_med'    : s['sold_price_sqm_med'],
                            #'sold_price_sqm_15'     : s['sold_price_sqm_15'],
                            #'sold_price_sqm_85'     : s['sold_price_sqm_85'],
                            'sold_area_avg'         : s['sold_area_avg'],
                            'sold_area_med'         : s['sold_area_med'],
                            #'sold_area_15'          : s['sold_area_15'],
                            #'sold_area_85'          : s['sold_area_85'],
                            'sold_rent_avg'         : s['sold_rent_avg'],
                            'sold_rent_med'         : s['sold_rent_med'],
                            #'sold_rent_15'          : s['sold_rent_15'],
                            #'sold_rent_85'          : s['sold_rent_85'],
                            'sold_daysbeforesold_avg' : s['sold_daysbeforesold_avg'].total_seconds() / (3600*24),
                            'sold_propertyage_avg' : s['sold_propertyage_avg']
                        })

                    if self.options['etlPeriodType'] == 'Weekly':
                        etlsold.weekofyear = dayFrom.isocalendar()[1]
                    elif self.options['etlPeriodType'] == 'Monthly':
                        etlsold.monthofyear = dayFrom.month
                    elif self.options['etlPeriodType'] == 'Quarterly':
                        etlsold.quarterofyear = int((dayFrom.month - 1) / 3)  + 1
                    etlsold.save()

        etls = EtlListingsDaily.objects
        if self.options['etlPeriodType'] == 'Weekly':
            etls = EtlListingsWeekly.objects
        elif self.options['etlPeriodType'] == 'Monthly':
            etls = EtlListingsMonthly.objects
        elif self.options['etlPeriodType'] == 'Quarterly':
            etls = EtlListingsQuarterly.objects
        elif self.options['etlPeriodType'] == 'Yearly':
            etls = EtlListingsYearly.objects

        etls.filter(record_firstdate__date = dayFrom, active_listings__isnull = True).update(active_listings=0)
        etls.filter(record_firstdate__date=dayFrom, sold_today__isnull=True).update(sold_today=0)
        return 0


    def finish(self, *args):
        return 0

#************************************************************************************





