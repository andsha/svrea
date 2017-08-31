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
import threading
import traceback

from django.db import transaction
from django.db.models import Func, Count, Q, F, Avg, Aggregate, When, Case, Min, Max, ExpressionWrapper, IntegerField, FloatField, Value
from django.db.models.functions import Coalesce
from svrea_script.models import Info, Log, Rawdata, Aux, Listings, Source, Address, Pricehistory
from svrea_etl.models import EtlListingsDaily, EtlListingsWeekly, EtlListingsMonthly, EtlListingsQuarterly, EtlListingsYearly
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
        self.threadPool = set()


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
        maxThreads = int(self.options['numThreads'])


        while dayFrom <= endofperiod:
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

            for s in ['listings', 'sold']:
                while len(self.threadPool) > maxThreads - 1:
                    if Aux.objects.get(key='AnalyzeAuxKey').value != 'run':
                        for th in self.threadPool:
                            th.run = False
                            while not th.is_alive():
                                time.sleep(0.1)
                        info.status = 'stopped'
                        info.save()
                        tolog(ERROR, 'script %s %s was stopped by %s' % (info.id, info.config, self.username))
                        return 1

                    for th in self.threadPool.copy():
                        if not th.is_alive():
                            if th.err != 0:
                                tolog(ERROR, '%s errors when analyzing %s %s for %s ' %(th.err, th.etlPeriodType, th.ptype, th.dayFrom))
                            self.threadPool.discard(th)

                    time.sleep(1)

                tolog(INFO, '%s %s analysis for %s' %(self.options['etlPeriodType'], s, dayFrom))
                thread = ETLThread(s, dayFrom, dayTo, self.options['etlPeriodType'], True)
                #tolog(INFO, 'thread:%s' %thread)
                thread.start()
                #tolog(INFO, 'thread')
                self.threadPool.add(thread)


            # (hist, created) = EtlHistory.objects.get_or_create(
            #     historydate__date = self.today,
            #     etldate = dayFrom,
            #     etlperiod = self.options['etlPeriodType'],
            #     defaults = {
            #         'historydate'   : self.today,
            #         'status'        : 'started'
            #     }
            # )
            #
            # if not created:
            #     if hist.status == 'done' and not self.forced:
            #         tolog(INFO, 'ETL already run for %s' %(dayFrom))
            #         return 1
            #     else:
            #         hist.historydate = self.today
            #         hist.status = 'started'
            #         hist.save()

            # if self.fill_listings_daily_stats(ptype, dayFrom, dayTo,self.options['etlPeriodType']) == 0:  #use dayFrom and DayTo
            #     hist.status = 'done'
            #     hist.save()
            # else:
            #     hist.status = 'error'
            #     hist.save()

            dayFrom = dayTo

        while len(self.threadPool) > 0:
            if Aux.objects.get(key='AnalyzeAuxKey').value != 'run':
                for th in self.threadPool:
                    th.run = False
                    while not th.is_alive():
                        time.sleep(0.1)
                info.status = 'stopped'
                info.save()
                tolog(ERROR, 'script %s %s was stopped by %s' % (info.id, info.config, self.username))
                return 1

            for th in self.threadPool.copy():
                if not th.is_alive():
                    if th.err != 0:
                        tolog(ERROR, '%s errors when analyzing %s %s for %s ' % (
                        th.err, th.etlPeriodType, th.ptype, th.dayFrom))
                    self.threadPool.discard(th)

            time.sleep(1)

        info.status = 'done'
        info.save()
        tolog(INFO, 'Analysis completed')
        return 0


#************************************************************************************

class ETLThread(threading.Thread):
    def __init__(self, ptype, dayFrom, dayTo, etlPeriodType, trun):
        threading.Thread.__init__(self)
        self.ptype = ptype
        self.dayFrom = dayFrom
        self.dayTo = dayTo
        self.etlPeriodType = etlPeriodType
        self.trun = trun
        self.err = 0


        self.listings_fields = [
            'active_listings',
            'listing_price_avg',
            'listing_price_med',
            'listing_price_sqm_avg',
            'listing_price_sqm_med',
            'listing_price_sqm_med',
            'listing_area_avg',
            'listing_area_med',
            'listing_rent_avg',
            'listing_rent_med'
        ]

        self.sold_fields = [
            'sold_today',
            'sold_price_avg',
            'sold_price_med',
            'sold_price_sqm_avg',
            'sold_price_sqm_med',
            'sold_price_sqm_med',
            'sold_area_avg',
            'sold_area_med',
            'sold_rent_avg',
            'sold_rent_med',
            'sold_daysbeforesold_avg',
            'sold_propertyage_avg'
        ]

        self.query_lfields = [
            'p_counts',
            'p_price_avg',
            'p_price_med',
            'p_price_sqm_avg',
            'p_price_sqm_med',
            'p_price_sqm_med',
            'p_area_avg',
            'p_area_med',
            'p_rent_avg',
            'p_rent_med'
        ]

        self.query_sfields = self.query_lfields + ['p_daysbeforesold_avg','p_propertyage_avg']
        #tolog(INFO, self.query_sfields)


    def run(self):

        geographic_types = ['county', 'municipality', 'country']
        property_types = ['Villa', 'Lägenhet']
        # logging.info('bebebe')

        for gtype in geographic_types:
            if not self.trun:
                return 0
            #tolog(INFO, gtype)
            try:

                qset = Listings.objects.values(
                    'address__county' if gtype == 'county' else 'address__municipality' if gtype == 'municipality' else 'address__country',
                    'propertytype') \
                    .filter(propertytype__in=property_types)
                #tolog(INFO, '1')
                if self.ptype =='listings':
                    qset = qset.filter(Q(datepublished__date__lt=self.dayTo) & (Q(dateinactive__isnull=True) | Q(dateinactive__date__gte=self.dayFrom)))
                else: # ptype == 'sold'
                    qset = qset.filter(Q(datesold__date__lt=self.dayTo) & Q(datesold__date__gte=self.dayFrom))
                #tolog(INFO, '2')
                qset = qset.annotate(p_counts=Count('booliid'),
                              p_price_avg=Avg('latestprice'),
                              p_price_med=Percentile(expression='latestprice', percentiles=0.5),
                              # listing_price_85=Percentile(expression='latestprice', percentiles=0.85),
                              # listing_price_15=Percentile(expression='latestprice', percentiles=0.15),
                              p_price_sqm_avg=Avg(
                                  F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),
                              p_price_sqm_med=Percentile(expression=(
                              F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),
                                                               percentiles=.5),
                              # listing_price_sqm_15=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.15),
                              # listing_price_sqm_85=Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact=0), then='livingarea'), default=None)),percentiles=.85),
                              p_area_avg=Avg('livingarea'),
                              p_area_med=Percentile(expression='livingarea', percentiles=.5),
                              # listing_area_15=Percentile(expression='livingarea', percentiles=.15),
                              # listing_area_85=Percentile(expression='livingarea', percentiles=.85),
                              p_rent_avg=Avg('rent'),
                              p_rent_med=Percentile(expression='rent', percentiles=.5),
                              # listing_rent_15=Percentile(expression='rent', percentiles=.15),
                              # listing_rent_85=Percentile(expression='rent', percentiles=.85),
                              )
                #tolog(INFO, '3')
                if self.ptype == 'sold':
                    qset = qset.annotate(
                              p_daysbeforesold_avg=Avg((Extract_date('datesold', dtype='epoch') - Extract_date('datepublished', dtype='epoch'))/(3600*24), output_field=FloatField()),
                              #p_propertyage_avg = Avg((F('datesold_sec') - F('datepublished_sec'))/(3600*24), output_field=FloatField())
                              p_propertyage_avg = Avg(Case(
                                  When(
                                      Q(constructionyear__isnull = False) & Q(constructionyear__gt = 1800) & Q(constructionyear__lt = 2100),
                                      then = Extract_date('datesold', dtype='year') - F('constructionyear')),
                                  default=None,
                                  output_field=FloatField()
                              ), output_field=FloatField())
                              )

                #tolog(INFO, '3')
                for idx, q in enumerate(qset):
                    #tolog(INFO, 'idx %s 1' %idx)
                    etllistings = EtlListingsDaily.objects
                    if self.etlPeriodType == 'Weekly':
                        etllistings = EtlListingsWeekly.objects
                    elif self.etlPeriodType == 'Monthly':
                        etllistings = EtlListingsMonthly.objects
                    elif self.etlPeriodType == 'Quarterly':
                        etllistings = EtlListingsQuarterly.objects
                    elif self.etlPeriodType == 'Yearly':
                        etllistings = EtlListingsYearly.objects

                    #tolog(INFO, 'idx %s 2' % idx)

                    d= dict(zip(
                            self.listings_fields if self.ptype == 'listings' else self.sold_fields,
                            [q[i] for i in (self.query_lfields if self.ptype == 'listings' else self.query_sfields)]
                            ))
                    gname = q[
                            'address__county' if gtype == 'county' else 'address__municipality' if gtype == 'municipality' else 'address__country']

                    #tolog(INFO, 'idx %s 3 %s' % (idx, q))

                    with transaction.atomic():
                        (etlquery, created) = etllistings.update_or_create(
                            record_firstdate=self.dayFrom,
                            geographic_type=gtype,
                            geographic_name=gname,
                            property_type=q['propertytype'],
                            defaults=d
                            )
                        #tolog(INFO, 'idx %s 4' % idx)
                        if self.etlPeriodType == 'Weekly':
                            etlquery.weekofyear = self.dayFrom.isocalendar()[1]
                        elif self.etlPeriodType == 'Monthly':
                            etlquery.monthofyear = self.dayFrom.month
                        elif self.etlPeriodType == 'Quarterly':
                            etlquery.quarterofyear = int((self.dayFrom.month - 1) / 3) + 1
                        etlquery.save()
                    #tolog(INFO, 'idx %s 5' % idx)

            except Exception as e:
                tolog(ERROR, 'Error while analysing %s %s for %s: %s\n %s' %(self.etlPeriodType, self.ptype, self.dayFrom, e, traceback.format_exc()[:2800]))
                tolog(ERROR, '%s' %q)
                self.err+=1
        #tolog(INFO, '4')
        etls = EtlListingsDaily.objects
        if self.etlPeriodType == 'Weekly':
            etls = EtlListingsWeekly.objects
        elif self.etlPeriodType == 'Monthly':
            etls = EtlListingsMonthly.objects
        elif self.etlPeriodType == 'Quarterly':
            etls = EtlListingsQuarterly.objects
        elif self.etlPeriodType == 'Yearly':
            etls = EtlListingsYearly.objects
        #tolog(INFO, '5')
        etls.filter(record_firstdate__date=self.dayFrom, active_listings__isnull=True).update(active_listings=0)
        #tolog(INFO, '6')
        etls.filter(record_firstdate__date=self.dayFrom, sold_today__isnull=True).update(sold_today=0)
        #tolog(INFO, '7')
        return 0




