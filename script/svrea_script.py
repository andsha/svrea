#!/usr/bin/env python3


import sys, os, threading
from urllib.request import urlopen
import time
from hashlib import sha1
import string
import json
import datetime
import logging
import random
import time
import re
from optparse import OptionParser
import shutil
import re

from script import pgUtil
import dj_database_url

from django.db.models import F,Q, Func

from svrea_script.models import Info, Log, Rawdata, Aux, Listings, Source, Address, Pricehistory






gCallerId = 'scr06as'
gUniqueKey = '3i0WnjAooYIHhgnyUKF597moNCYnt449kZbK3YAR'

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gDBStruct = BASE_FOLDER + '/script/DBStruct.cfg'
gDBFillRules = BASE_FOLDER + '/script/DBFillRules.cfg'

gLimit = 3

UPDATE = 1000
INSERT = 1001

CREATE = 2000
DELETE = 2001
TYPE = 2002

LISTINGS = 3001
SOLD = 3002
LASTSOLD = 3003
LASTSOLD = 3003

class Datetime_to_date(Func):
    function = 'EXTRACT'
    template = '%(expressions)s::date'


def err(obj = None, msg = None):

        if msg is not None:
            logging.error(msg)

        if obj is not None:
            obj.pgcon.close()

            try:
                obj.error += 1
            except NameError:
                return None
            else:
                return obj.error

# class DataBase():
#
#     def __init__(self, connection):
#         self.pgcon = connection
#         #self.fdbstruct = fdbstruct # file with version 0 DB structure
#         #self.frules = frules       # file with filling rules
#
#         #self.schema = self.getSchema()
#         # self.version = self.getVersion()
#
#         # self.tableDic = self.getTableDic()
#         # self.primaryKeys = self.getPrimaryKeys()
#         # self.foreignKeys = self.getForeignKeys()
#         self.error = 0
#         self.date = ''
#
#         self.source = None
#
#
#     def uploadData(self, info = None):
#         data_to_upload = Rawdata.objects.filter(uploaded__exact = False).\
#             annotate(downloaded_date=Datetime_to_date('downloaded')).\
#             order_by('downloaded_date', '-type', 'areacode')
#
#         for data in data_to_upload:
#             today = data.downloaded.date()
#             if data.type == 'sold':
#                 Listings.objects.filter(isactive=True). \
#                     update(isactive = False, dateinactive = today)
#             #print(data.downloaded, data.uploaded, data.type, data.areacode)
#
#             for listing in data.rawdata[data.type]:
#                 if Aux.objects.get(key='UploadAuxKey').value != 'run':
#                     info.status = 'stopped'
#                     info.save()
#                     return 1
#
#                 # *********************************************
#
#                 sourceid = listing['source']['id']
#                 sourcename = listing['source']['name']
#                 sourcetype = listing['source']['type']
#                 sourceurl = listing['source']['url']
#                 #print(sourceid, sourcename,sourcetype, sourceurl )
#
#                 (source, source_created) = Source.objects.get_or_create(
#                     sourceid=sourceid,
#                     name=sourcename,
#                     sourcetype=sourcetype,
#                     url=sourceurl
#                 )
#
#                 #####################################################
#
#                 house = None
#                 street = None
#                 city = None
#                 county = None
#                 municipality = None
#                 areaname = None
#
#                 if 'streetAddress' in listing['location']['address']:
#                     house = re.search('\\d+[^ ]*', listing['location']['address']['streetAddress'])
#
#                     if house is not None:
#                         house = house.group(0)
#                     else:
#                         house = None
#
#                     street = re.sub('\\d+[^ ]*', '', listing['location']['address']['streetAddress'])
#
#                 if 'city' in listing['location']['address']:
#                     city = listing['location']['address']['city']
#                 if 'countyName' in listing['location']['region']:
#                     county = listing['location']['region']['countyName']
#                 if 'municipalityName' in listing['location']['region']:
#                     municipality = listing['location']['region']['municipalityName']
#                     if city is None:
#                         city = municipality
#                 if 'namedAreas' in listing['location']:
#                     areaname = listing['location']['namedAreas']
#
#                 address, address_created = Address.objects.update_or_create(
#                     house=house,
#                     street=street,
#                     city=city,
#                     municipality=municipality,
#                     county=county,
#                     defaults={
#                         "areaname": areaname
#                     }
#                 )
#
#                 #######################################################
#                 plotarea = None
#                 additionalarea = None
#                 livingarea = None
#                 floor = None
#                 isnewconstruction = False
#                 isactive = False
#                 datesold = None
#                 dateinactive = None
#                 latestprice = None
#                 rent = None
#                 constructionYear = None
#                 rooms = None
#                 soldprice = None
#                 listprice = None
#
#
#                 if 'rent' in listing:
#                     rent = int(listing['rent'])
#                 if 'constructionYear' in listing:
#                     constructionYear = listing['constructionYear']
#                 if 'rooms' in listing:
#                     rooms = listing['rooms']
#                 if 'plotArea' in listing:
#                     plotarea = listing['plotArea']
#                 if 'additionalArea' in listing:
#                     additionalarea = listing['additionalArea']
#                 if 'livingArea' in listing:
#                     livingarea = listing['livingArea']
#                 if 'floor' in listing:
#                     floor = listing['floor']
#                 if 'isNewConstruction' in listing:
#                     isnewconstruction = listing['isNewConstruction']
#                 if data.type == 'listings':
#                     isactive = True
#                     if 'listPrice' in listing:
#                         listprice = int(listing['listPrice'])
#                     latestprice = listprice
#                 if data.type == 'sold':
#                     isactive = False
#                     if 'soldPrice' in listing:
#                         soldprice = int(listing['soldPrice'])
#                     latestprice = soldprice
#                     datesold = datetime.datetime.strptime(listing['soldDate'], '%Y-%m-%d')
#                     dateinactive = datesold
#
#                 # print(listing['booliId'],
#                 #       listing['published'],
#                 #       listing['location']['position']['latitude'],
#                 #       listing['location']['position']['longitude'],
#                 #       constructionYear,
#                 #       rent,
#                 #       listing['url'],
#                 #       rooms,
#                 #       listing['objectType'],
#                 #       plotarea,
#                 #       additionalarea,
#                 #       livingarea,
#                 #       floor,
#                 #       isnewconstruction,
#                 #       datesold,
#                 #       isactive,
#                 #       latestprice,
#                 #       dateinactive)
#
#
#                 (listings, listings_created) = Listings.objects.update_or_create(
#                     booliid  = listing['booliId'],
#                     defaults = {
#                         "datepublished"     : listing['published'],
#                         "source"            : source,
#                         "address"           : address,
#                         "latitude"          : listing['location']['position']['latitude'],
#                         "longitude"         : listing['location']['position']['longitude'],
#                         "constructionyear"  : constructionYear,
#                         "rent"              : rent,
#                         "url"               : listing['url'],
#                         "rooms"             : rooms,
#                         "propertytype"      : listing['objectType'],
#                         "plotarea"          : plotarea,
#                         "additionalarea"    : additionalarea,
#                         "livingarea"        : livingarea,
#                         "floor"             : floor,
#                         "isnewconstruction" : isnewconstruction,
#                         "datesold"          : datesold,
#                         "isactive"          : isactive,
#                         "latestprice"       : latestprice,
#                         "dateinactive"      : dateinactive
#                     }
#                 )
#
#                 priceobj = Pricehistory.objects.filter(booliid = listing['booliId']).order_by('-date')
#
#                 newprice = latestprice
#                 newdate = today
#                 newissoldprice = False
#                 createnewprice = True
#
#                 if priceobj.count() > 0:
#                     priceobj = priceobj[0]
#                     if priceobj.issoldprice: # last is sold
#                         if data.type == 'sold': # current is sold
#                             if priceobj.date.date() == datesold.date():
#                                 if priceobj.price == latestprice:
#                                     createnewprice = False
#                                 else:
#                                     priceobj.date = datesold.date()
#                                     priceobj.price = latestprice
#                                     priceobj.save()
#                                     createnewprice = False
#                             else:
#                                 priceobj.date = datesold.date()
#                                 priceobj.price = latestprice
#                                 priceobj.save()
#                                 createnewprice = False
#                     else: # last is listing
#                         if data.type == 'sold': # current is sold
#                             newissoldprice = True
#                         else: # current is listing
#                             if latestprice == priceobj.price:
#                                 createnewprice = False
#                 else:
#                     if data.type == 'sold':
#                         newissoldprice = True
#
#                 if createnewprice:
#                     newpriceobj = Pricehistory(
#                         booliid = listings,
#                         price = newprice,
#                         date = newdate,
#                         issoldprice = newissoldprice
#                     )
#                     newpriceobj.save()
#
#             data.uploaded = True
#             data.save()
#
#         aux = Aux.objects.get(key='UploadAuxKey')
#         aux.value = 'complete'
#         aux.save()
#
#         info.status = 'done'
#         info.save()
#



WARNING = 1101
ERROR = 1102
INFO = 1103


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

        if 'forced' in self.options and self.options['forced']:
             self.forced = True
             self.options.pop('forced', None)

        self.username = username


    def run(self):
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
        #print(self.options)
        if 'download' in self.options:
            tolog(INFO, ("Downloading %s" %self.options['download']))
            a = Aux.objects.update_or_create(key = 'DownloadAuxKey', defaults={"key" : "DownloadAuxKey",
                                                                                "value" : "run"})
            err += self.getDataFromWeb(info = info, latest = True if 'downloadLast' in self.options else False)
      # -----------------------------------------------------------------------------------
        if 'upload' in self.options and self.options['upload']:
            tolog(INFO, 'Uploading data')
            a = Aux.objects.update_or_create(key='UploadAuxKey', defaults={"key": "UploadAuxKey",
                                                                         "value": "run"})
            err += self.uploadData(info=info)

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
        area_list = ['64',  # Skane
                     '160', #Halland
                     # '23', # vastra gotalands
                     # '2',  # Stockholm lan
                     # '783', # Kronobergs lan
                     # '45', #Blekinge lan
                     # '381', # Kalmar
                     # '153', # Jonkoping
                     # '253', # ostergotland lan
                     # '26', # sodermanlands lan
                     # '145', # Blekinge lan
                     ]  #

        for idx, area in enumerate(area_list):
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

            while 1:
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

                data = urlopen(url).read().decode('utf-8')
                dic = json.loads(data)
                raw_data = Rawdata(areacode=area, rawdata=dic, type=self.options['download'])
                raw_data.save()
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
        data_to_upload = Rawdata.objects.filter(uploaded__exact=False). \
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

                (source, source_created) = Source.objects.get_or_create(
                    sourceid=sourceid,
                    name=sourcename,
                    sourcetype=sourcetype,
                    url=sourceurl
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

            data.uploaded = True
            data.save()

        # aux = Aux.objects.get(key='UploadAuxKey')
        # aux.value = 'complete'
        # aux.save()

        info.status = 'done'
        info.save()



# if __name__ == "__main__":
#     prog = svrea_script()
#     sys.exit(prog.run())