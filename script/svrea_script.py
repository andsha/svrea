#!/usr/bin/env python3


import os,sys
from urllib.request import urlopen
from hashlib import sha1
import string
import json
import datetime
import random
import time
import re

from django.db.models import Func, Count, Q, F, Avg, Aggregate, When, Case
from django.db.models.functions import Coalesce
from svrea_script.models import Info, Log, Rawdata, Aux, Listings, Source, Address, Pricehistory
from svrea_etl.models import EtlHistory, EtlListings
import logging

gCallerId = 'scr06as'
gUniqueKey = '3i0WnjAooYIHhgnyUKF597moNCYnt449kZbK3YAR'

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gDBStruct = BASE_FOLDER + '/script/DBStruct.cfg'
gDBFillRules = BASE_FOLDER + '/script/DBFillRules.cfg'

WARNING = 1101
ERROR = 1102
INFO = 1103

area_list = [['64', 'Skane'],
             ['160', 'Halland'],
             ['23', 'Vastra Gotalands'],
             ['2',  'Stockholm lan'],
             ['783', 'Kronobergs lan'],
             ['45', 'Blekinge lan'],
             ['381', 'Kalmar'],
             ['153', 'Jonkoping'],
             ['253', 'Ostergotland lan'],
             ['26', 'Sodermanlands lan'],
             ]
area_list.sort(key = lambda x: int(x[0]) )


class Datetime_to_date(Func):
    function = 'EXTRACT'
    template = '%(expressions)s::date'


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

        #print(today_scripts)
        for s in today_scripts:
            #print(s.config, self.options, s.config == self.options )
            if s.config == self.options:
                runtoday = True
                if s.status == 'done' and not self.forced: # if succesfully run before
                    st = 'already run for %s' %self.options
                    tolog(INFO, st)
                    return 1
                else:
                    s.status = 'started'
                    s.save()
                    info = s
                    break

        if not runtoday:
            l = Info(user_name = self.username,
                     config = self.options,
                     status = 'started')
            l.save()
            info = l
        # _________________________________________________________________________________________
        if 'download' in self.options:
            tolog(INFO, ("Downloading %s" %self.options['download']))
            a, created = Aux.objects.update_or_create(key = 'DownloadAuxKey', defaults={"key" : "DownloadAuxKey",
                                                                                "value" : "run"})
            err += self.getDataFromWeb(info = info, latest = True if 'downloadLast' in self.options and self.options['downloadLast'] else False)
        # -----------------------------------------------------------------------------------
        if 'upload' in self.options and self.options['upload']:
            tolog(INFO, 'Uploading data')
            a, created = Aux.objects.update_or_create(key='UploadAuxKey', defaults={"key": "UploadAuxKey",
                                                                         "value": "run"})
            err += self.uploadData(info=info)
        # -----------------------------------------------------------------------------------
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

                tolog(INFO, "%s out of %s" % (offset / limit + 1, int(maxcount / limit) + 1))
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
                        "datepublished": listing['published'],
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
        datefrom = datetime.datetime.strptime(self.options['etlRange'].split(':')[0], "%Y-%m-%d")
        dateto = datetime.datetime.strptime(self.options['etlRange'].split(':')[1], "%Y-%m-%d")
        today = datefrom

        while today <= dateto:
            for idx, stage in enumerate(stages):
                (hist, created) = EtlHistory.objects.get_or_create(
                    historydate__date = self.today,
                    etldate = today,
                    stage = stage,
                    defaults = {
                        'historydate'   : self.today,
                        'stage'         : stage,
                        'status'        : 'started'
                    }
                )

                if not created:
                    if hist.status == 'done' and not self.forced:
                        tolog(INFO, '%s Already run for %s' %(stage, self.today))
                        return 1
                    else:
                        hist.historydate = self.today
                        hist.status = 'started'
                        hist.save()

                if getattr(self, stage)(today) == 0:
                    hist.status = 'done'
                    hist.save()
                else:
                    hist.status = 'error'
                    hist.save()

            today += datetime.timedelta(days=1)

        info.status = 'done'
        info.save()
        return 0


    def init(self, *args):
        return 0


    def check_tables(self, *args):
        return 0


    def fill_listings_daily_stats(self, today):
        geographic_types = ['county', 'municipality']
        #logging.info('bebebe')

        for gtype in geographic_types:
            listing = Listings.objects.values('address__county' if gtype == 'county' else 'address__municipality')\
                .filter(Q(datepublished__date__lte = today) &
                        (Q(dateinactive__isnull=True) | Q(dateinactive__gt=today)))\
                .annotate(listing_counts=Count('booliid'),
                          listing_price_avg = Avg('latestprice'),
                          listing_price_med = Percentile(expression='latestprice', percentiles=0.5),
                          listing_price_85=Percentile(expression='latestprice', percentiles=0.85),
                          listing_price_15=Percentile(expression='latestprice', percentiles=0.15),
                          listing_price_sqm_avg = Avg(F('latestprice') / Case(When(~Q(livingarea__exact = 0), then='livingarea'), default=None)),
                          listing_price_sqm_med = Percentile(expression=(F('latestprice') / Case(When(~Q(livingarea__exact = 0), then='livingarea'), default=None)), percentiles=.5)
                          )

            for l in listing:

                (etllisting, created) = EtlListings.objects.update_or_create(
                    record_date             = today,
                    geographic_type         = gtype,
                    geographic_name         = l['address__county' if gtype == 'county' else 'address__municipality'],
                    defaults                = {
                        'active_listings' : l['listing_counts'],
                        'listing_price_avg' : l['listing_price_avg'],
                        'listing_price_med' : l['listing_price_med'],
                        'listing_price_85' : l['listing_price_85'],
                        'listing_price_15' : l['listing_price_15'],
                        'listing_price_sqm_avg' : l['listing_price_sqm_avg'],
                        'listing_peice_sqm_med' : l['listing_price_sqm_med']
                    }
                )


            #     listing_price_sqm_avg
            #     listing_price_sqm_med
            #     listing_price_sqm_85 =
            #     listing_price_sqm_15 =
            #     listing_area_avg =
            #     listing_area_max =
            #     listing_area_min =
            #     listing_area_med =
            #     listing_rent_avg =
            #     listing_rent_max =
            #     listing_rent_min =
            #     listing_rent_med =
            #
                # sold_today
            #     sold_price_avg =
            #     sold_price_med =
            #     sold_price_85 =
            #     sold_price_15 =
            #     sold_price_sqm_avg =
            #     sold_price_sqm_med =
            #     sold_price_sqm_85 =
            #     sold_price_sqm_15 =
            #     sold_area_avg =
            #     sold_area_max =
            #     sold_area_min =
            #     sold_area_med =
            #     sold_rent_avg =
            #     sold_rent_max =
            #     sold_rent_min =
            #     sold_rent_med =
            # )

        return 0


    def finish(self, *args):
        return 0





