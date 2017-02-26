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
import re
from optparse import OptionParser
import shutil
import re

from script import pgUtil
import dj_database_url

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

class DataBase():

    def __init__(self, connection, frules = None):
        self.pgcon = connection
        #self.fdbstruct = fdbstruct # file with version 0 DB structure
        self.frules = frules       # file with filling rules

        #self.schema = self.getSchema()
        # self.version = self.getVersion()

        # self.tableDic = self.getTableDic()
        # self.primaryKeys = self.getPrimaryKeys()
        # self.foreignKeys = self.getForeignKeys()
        self.error = 0
        self.date = ''

        self.source = None

        #print("select", self.pgcon.run("SELECT 10"))


    # def getSchema(self,fdbstruct = None):
    #     if fdbstruct is None:
    #         fdbstruct = self.fdbstruct
    #
    #     jsonData = open(self.fdbstruct).read()
    #     dbstruct = json.loads(jsonData)
    #
    #     schema = dbstruct['SCHEMANAME']
    #     return schema


    # #   Get current version of schema
    # def getVersion(self):
    #     sql = """SELECT 1 FROM information_schema.tables
    #               WHERE table_schema = '%s'
    #               AND table_name = 'info' """ % self.schema
    #
    #     res = self.pgcon.run(sql, True)
    #
    #     if len(res) == 0:
    #         return None
    #
    #     sql = """SELECT version FROM "%s".info where date = (SELECT MAX(date) FROM "%s".info)""" % (self.schema, self.schema)
    #     res = self.pgcon.run(sql, True)
    #     return res[0][0]


    # def getTableDic(self):
    #     sql = """SELECT 1 FROM information_schema.tables
    #               WHERE table_schema = '%s'
    #               AND table_name = 'info' """ % self.schema
    #
    #     res = self.pgcon.run(sql, True)
    #
    #     if len(res) == 0:
    #         return {}
    #
    #     sql = """SELECT tabledic FROM "%s".info where version = %s""" % (
    #     self.schema, self.version)
    #     res = self.pgcon.run(sql, True)
    #     return res[0][0]


    # def getPrimaryKeys(self):
    #     sql = """SELECT 1 FROM information_schema.tables
    #               WHERE table_schema = '%s'
    #               AND table_name = 'info' """ % self.schema
    #
    #     res = self.pgcon.run(sql, True)
    #
    #     if len(res) == 0:
    #         return []
    #
    #     sql = """SELECT primarykey FROM "%s".info where version = %s""" % (
    #         self.schema, self.version)
    #     res = self.pgcon.run(sql, True)
    #     return res[0][0].split(',')


    # def getForeignKeys(self):
    #     sql = """SELECT 1 FROM information_schema.tables
    #               WHERE table_schema = '%s'
    #               AND table_name = 'info' """ % self.schema
    #
    #     res = self.pgcon.run(sql, True)
    #
    #     if len(res) == 0:
    #         return {}
    #
    #     sql = """SELECT foreignkey FROM "%s".info where version = %s""" % (
    #         self.schema, self.version)
    #     res = self.pgcon.run(sql, True)
    #     return res[0][0]


    # def updateDB(self, fdbstruct = None, toVersion = -1, startOver = False):
    #
    #     if fdbstruct is None:
    #         fdbstruct = self.fdbstruct
    #     else:
    #         self.fdbstruct = fdbstruct
    #
    #     if toVersion == -1:
    #         toVersion = self.getMaxVersion(fdbstruct)
    #
    #     jsonData = open(fdbstruct).read()
    #     dbstruct = json.loads(jsonData)
    #
    #     if 'SCHEMANAME' not in dbstruct:
    #         return err("SCHEMANAME could not be found in config")
    #
    #     schema = dbstruct['SCHEMANAME']
    #     self.schema = schema
    #
    #     # self.version = self.getVersion()
    #     fromVersion = self.version
    #
    #     if self.version is None or startOver is True:
    #         fromVersion = -1
    #
    #     for version in range(fromVersion, toVersion):
    #         updversion = version + 1
    #
    #         #print ('updversion', updversion)
    #
    #         if updversion == 0: # new DB
    #             logging.info('drop schema and start over')
    #             sql = "DROP SCHEMA IF EXISTS %s CASCADE" % schema
    #             res = self.pgcon.run(sql)
    #
    #             if res != 0:
    #                 return err("Error while dropping schema %s" % schema)
    #
    #             logging.info("Creating SCHEMA %s" % schema)
    #             sql = "CREATE SCHEMA %s;" % schema
    #             res = self.pgcon.run(sql)
    #
    #             if res != 0:
    #                 return err("Error while creating schema %s" % schema)
    #
    #             self.tableDic = {}
    #             self.primaryKeys = []
    #             self.foreignKeys = {}
    #
    #         dbstruct = self.getDBStruct(uversion = updversion)
    #         #print (updversion, dbstruct)
    #         #foreignKeys = {}
    #         #primaryKeys = []
    #
    #         if 'TABLES' not in dbstruct:
    #             continue
    #
    #         for t in dbstruct['TABLES']:
    #             if 'NAME' not in t:
    #                 return err('No table name provided in %s. Table name should be called "NAME"' % t)
    #
    #             table = t['NAME']
    #
    #             #print (self.tableDic)
    #             if 'COLUMNS' in t:
    #                 if table in self.tableDic:
    #                     sql = """ALTER TABLE "%s"."%s" """ %(schema,table)
    #
    #
    #                     for c in t['COLUMNS']:
    #                         column = c['NAME']
    #
    #                         if column in self.tableDic[table]:
    #                             if 'ACTION' in c and c['ACTION'] == 'DELETE':
    #                                 sql += """DROP "%s", """ %column
    #                                 self.tableDic[table].pop(column)
    #
    #                                 if "%s.%s" %(table, column) in self.foreignKeys:
    #                                     self.foreignKeys.pop('%s.%s' %(table,column))
    #
    #                                 if "%s.%s" %(table, column) in self.primaryKeys:
    #                                     self.primaryKeys.remove("%s.%s" %(table, column))
    #
    #                             elif 'ACTION' in c and c['ACTION'] != 'TYPE':
    #                                 logging.error("undefined column operation")
    #                             else:
    #                                 ctype = c['TYPE']
    #                                 sql += """ALTER "%s" TYPE %s, """ %(column, ctype)
    #                                 self.tableDic[table][column] = ctype
    #                         elif 'ACTION' in c and c['ACTION'] == 'CREATE' or 'ACTION' not in c:
    #                             ctype = c['TYPE']
    #                             sql += """ADD "%s" %s  """ %(column, ctype)
    #                             self.tableDic[table][column] = ctype
    #
    #                             if 'CONSTRAINT' in c:
    #                                 if c['CONSTRAINT'] == 'PRIMARY KEY':
    #                                     sql += ' CONSTRAINT %s PRIMARY KEY ' % (t['NAME'] + 'key')
    #                                     self.primaryKeys.append('%s.%s' % (table, column))
    #                                 else:
    #                                     sql += ' %s' % c['CONSTRAINT']
    #
    #                             sql += ','
    #
    #                         if 'FOREIGN KEY' in c:
    #                             fkey = c['FOREIGN KEY']
    #                             self.foreignKeys['%s.%s' % (table, column)] = fkey
    #
    #                     sql = sql.rstrip(', ')
    #
    #                 else:
    #                     sql = """CREATE TABLE "%s"."%s"(""" % (schema, table)
    #                     self.tableDic["%s" % table] = {}
    #
    #                     for c in t['COLUMNS']:
    #                         column = c['NAME']
    #                         #print (table, column)
    #                         ctype = c['TYPE']
    #                         sql += ' "%s" %s ' % (column, ctype)
    #                         self.tableDic["%s" % table]["%s" % column] = ctype
    #
    #                         if 'FOREIGN KEY' in c:
    #                             fkey = c["FOREIGN KEY"]
    #                             self.foreignKeys["%s.%s" % (table, column)] = fkey
    #
    #                         if 'CONSTRAINT' in c:
    #                             if c['CONSTRAINT'] == 'PRIMARY KEY':
    #                                 sql += ' CONSTRAINT %s PRIMARY KEY ' % (t['NAME'] + 'key')
    #                                 self.primaryKeys.append('%s.%s' % (table, column))
    #                             else:
    #                                 sql += ' %s' % c['CONSTRAINT']
    #                         sql += ','
    #                     sql = sql.rstrip(', ')
    #                     sql += ')'
    #
    #                 #print (sql)
    #                 res = self.pgcon.run(sql)
    #
    #                 if res != 0:
    #                     return err("Error while creating table %s%s" % (schema, t))
    #
    #             if 'INDEXES' in t:
    #                 for i in t['INDEXES']:
    #                     idxname = ''
    #                     if "NAME" in i:
    #                         idxname = i['NAME']
    #                     else:
    #                         idxname = "%sidx" % i['COLUMNS'][0]
    #
    #                     sql = """CREATE INDEX  %s ON "%s"."%s" (""" % (idxname, schema, table)
    #
    #                     if 'COLUMN' not in i:
    #                         return err("No information about indexes in config")
    #
    #                     for col in i['COLUMN']:
    #                         sql += '"%s",' % col
    #
    #                     sql = sql.rstrip(',')
    #                     sql += ')'
    #
    #
    #                     res = self.pgcon.run(sql)
    #
    #                     if res != 0:
    #                         return err("Error while creating index %s" % idxname)
    #
    #         for fkey in self.foreignKeys:  # only one level of dependence
    #             if self.foreignKeys[fkey] in self.foreignKeys:
    #                 return err("Interdependent Foreign Key '%s' : '%s'" % (fkey, self.foreignKeys[fkey]))
    #
    #         #self.foreignKeys = foreignKeys
    #         #self.primaryKeys = primaryKeys
    #
    #         #print('primaryKeys:', self.primaryKeys)
    #         #print('foreignKeys:', self.foreignKeys)
    #         #print('tableDic', self.tableDic)
    #
    #         # create auxilary tables
    #
    #         sql = """CREATE TABLE IF NOT EXISTS "%s"."info" (version    int,
    #                                                         date        timestamp,
    #                                                         tabledic    json,
    #                                                         foreignkey  json,
    #                                                         primarykey  varchar(2000))""" % schema
    #         res = self.pgcon.run(sql)
    #
    #         sql = """INSERT INTO "%s".info VALUES (%s,'%s', '%s', '%s', '%s')
    #               """ %(schema, updversion,datetime.datetime.now(), ('%s' %self.tableDic).replace("'",'"'), ('%s' %self.foreignKeys).replace("'", '"'), ",".join(self.primaryKeys))
    #         res = self.pgcon.run(sql)
    #
    #         sql = """CREATE TABLE IF NOT EXISTS "%s".history   (id     int PRIMARY KEY,
    #                                                             date    timestamp DEFAULT now(),
    #                                                             script  varchar(200),
    #                                                             status  varchar(2000))""" %self.schema
    #         res = self.pgcon.run(sql)



    def uploadData(self):
        data_to_upload = Rawdata.objects.filter(uploaded__exact = False)

        for data in data_to_upload:
            for listing in data.rawdata[data.type]:
                source, soure_created = Source.objects.get_or_create(
                    sourceid    = listing['source']['id'],
                    name        = listing['source']['name'],
                    sourcetype  = listing['source']['type'],
                    url         = listing['source']['url']
                )

                # *********************************************
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
                if 'namedAreas' in listing['location']:
                    areaname = listing['location']['namedAreas']

                try:
                    address = Address.objects.get(
                        house           = house,
                        street          = street,
                        city            = city,
                        county          = county,
                    )
                except Address.DoesNotExist:
                    address = Address(
                        house           = house,
                        street          = street,
                        city            = city,
                        municipality    = municipality,
                        county          = county,
                        areaname        = areaname
                    )
                    address.save()

                Listings.objects.update_or_create(
                    booliid             = listing['booliId'],
                    datepublished       = listing['published'],
                    sourceid            = source,
                    addressid           = address
                )

            # {"url": "https://www.booli.se/annons/2249713",
            # "rent": 2774, "floor": 3, "rooms": 1,
            # "source": {"id": 204,
            #           "url": "http://www.maklarhuset.se/",
            #           "name": "Mäklarhuset",
            #           "type": "Broker"},
            # "booliId": 2249713,
            # "location": { "region": {  "countyName": "Skåne län",
            #                           "municipalityName": "Trelleborg"},
            #               "address": {"city": "Trelleborg",
            #                           "streetAddress": "Borggården 7"},
            #               "distance": {"ocean": 737},
            #               "position": {"latitude": 55.37551117,
            #                             "longitude": 13.17156029},
            #               "namedAreas": ["Trelleborg"]},
            # "soldDate": "2017-02-05",
            # "listPrice": 419000,
            # "published": "2017-01-30 21:09:14",
            # "soldPrice": 650000,
            # "livingArea": 36.8,
            # "objectType": "Lägenhet",
            # "constructionYear": 1948}

    # booliid = models.IntegerField(primary_key=True)
    # datepublished = models.DateTimeField(db_index=True)
    # sourceid = models.ForeignKey('Source', on_delete=models.CASCADE)
    # addressid = models.ForeignKey('Address', on_delete=models.CASCADE)
    # latitude = models.DecimalField(max_digits=10, decimal_places=8)
    # longitude = models.DecimalField(max_digits=10, decimal_places=8)
    # constructionyear = models.IntegerField()
    # rent = models.IntegerField()
    # url = models.CharField(max_length=250)
    # rooms = models.CharField(max_length=10)
    # propertytype = models.CharField(max_length=50)
    # plotarea = models.DecimalField(max_digits=5, decimal_places=1)
    # additionalarea = models.DecimalField(max_digits=5, decimal_places=1)
    # livingarea = models.DecimalField(max_digits=5, decimal_places=1)
    # floor = models.CharField(max_length=10)
    # isnewconstruction = models.BooleanField()
    # datesold = models.DateTimeField()
    # isactive = models.BooleanField(db_index=True)
    # dateinactive = models.DateTimeField()
    # latestprice = models.IntegerField()


    def qq(self):

        for dic in data: # individual data entry from json library
            valueDic = {}
            uniqueDic = {}
            skipTable = []
            skipColumn = []
            #print("________another listing________")

            for table in self.tableDic: # for each table from list of all tables
                valueDic[table] = {}

                for column in self.tableDic[table]: # for each column in table
                    #print ('\n',table, column)
                    ctype = self.tableDic[table][column]

                    if '%s.%s' %(table, column) in rules: # if rule for this column exists in rules dictionary

                        rule = rules['%s.%s' %(table, column)] # get rule

                        # _________________ working with column keywords _______________

                        keylist = rule.split('##')  # search for keywords
                                                    # rule has following form:
                                                    # "_KEYWORD_##KEYVALUE1##KEYVALUE2##...##PATH"
                                                    # where _KEYWORD_ is always first
                        #print("#1", plist)

                        keyword = None
                        keyvalue = None

                        if len(keylist) != 1:
                            keyword = keylist[0] # always first
                            keyvalue = keylist[1:] # anything in between keyword and path
                            #path = keylist[-1] # always last
                        else:
                            keyvalue = keylist

                        value = ''
                        #print(keyword, keyvalue)

                        if keyword is None: # if no keywords, then get value according to rule
                            value = self.getDicValue(dic, keyvalue[0])
                            #print(type(value))
                            if type(value) is str:
                                value = value.replace("'", "''")

                        elif keyword == '_REGEX_':
                            st = self.getDicValue(dic, keyvalue[-1])
                            #print(st)

                            if st is None:
                                value = ''
                            else:
                                s = re.search(keyvalue[0],st)
                                #print(st, s)

                                if s is not None:
                                    value = s.group(1)
                                else:
                                    value = ''

                        elif keyword == '_REGEX_REP_':
                            st = self.getDicValue(dic, keyvalue[-1])

                            if st is None:
                                value = ''
                            else:
                                s = re.sub(keyvalue[0], '', st)

                                if s is not None:
                                    value = s
                                else:
                                    value = ''

                        elif keyword == '_UNIQUE_NUMBER_':
                            if '%s.%s' %(table,column) not in uniqueDic:
                                uniqueDic['%s.%s' %(table,column)] = []

                            for col in keyvalue[0].split(','):
                                uniqueDic['%s.%s' %(table,column)].append(col)

                        elif keyword == '_IFEXISTS_':
                            #print (keyvalue)
                            value = self.getDicValue(dic, keyvalue[0])

                            #print (value)
                            if value is None:
                                (val, specialKey) = self.checkKey(keyvalue[2])
                            else:
                                if keyvalue[1] == '':
                                    val = value
                                    specialKey = True
                                    #print(val)
                                else:
                                    (val, specialKey) = self.checkKey(keyvalue[1])

                            if specialKey is True:
                                value = val
                            else:
                                value = self.getDicValue(dic, val)

                            #print(value)

                        elif keyword == '_SKIPCOLUMN_':
                            skipColumn.append('%s.%s' %(table, column))

                        else: #default
                            logging.warning('Unknown keyword %s' %keyword)
                            value = None
                    else:
                        value = None # if no rule exists in dictionary for this column, value is None

                    #print(table, column, value, rule)

                    if value is None:
                        if ctype == 'int' or 'decimal' or 'boolean' or 'serial':
                            value = 'NULL'
                        else:
                            value = ''

                    valueDic[table][column] = value


                    #print(self.primaryKeys)
                    #print(table,column)

            # treat Unique constraints ____________________________________________

            #print("Unique Dic:",uniqueDic)

            for tab in uniqueDic:
                [t,c] = tab.split('.')

                sql = """SELECT "%s" FROM "%s"."%s" WHERE""" %(c,self.schema,t)

                for col in uniqueDic[tab]:
                    val = valueDic[t][col]
                    sql += """ "%s" %s AND""" %(col,("='%s'" %val) if val !='NULL' else 'is NULL')

                sql = sql[:-4]
                res = self.pgcon.run(sql,True)

                #print(sql)
                #print(res)

                if len(res) == 0:
                    sql = """SELECT max("%s") FROM "%s"."%s" """ %(c,self.schema,t)
                    res = self.pgcon.run(sql, True)

                    if res[0][0] is None:
                        value = 1
                    else:
                        value = res[0][0] + 1
                else:
                    value = res[0][0]

                #print ("idx", idx)
                #print('value2',value)
                valueDic[t][c] = value

            #print('valueDic', valueDic)

            # treat Foreign Keys _________________________________________________

            #print('foreigh keys:', self.foreignKeys)
            for fkey in self.foreignKeys:
                table, column = fkey.split('.')
                ftable, fcolumn = self.foreignKeys[fkey].split('.')

                if ftable in valueDic and fcolumn in valueDic[ftable]:
                    valueDic[table][column] = str(valueDic[ftable][fcolumn])
                else:
                    return err("Missing foreign table of column '%s' : '%s'" %(ftable, fcolumn), self)

            #__Treat table keywords_____________________________________________________________________

            for table in valueDic:
                if table in rules:
                    #print(table, 'in rules')
                    rule = rules[table]
                    keylist = rule.split('##')  # search for keywords
                    keyword = None
                    keyvalue = None

                    if len(keylist) != 1:
                        keyword = keylist[0]
                        keyvalue = keylist[1:]
                        #path = keylist[-1]
                    else:
                        keyvalue = keylist

                    # this keyword is booli-specific.
                    if keyword == '_SKIPIFSAMEASLATEST_':
                        value = valueDic[table][keyvalue[0]]
                        sql = """SELECT id, "%s", "%s", "%s", "%s" FROM "%s"."%s" WHERE  "%s" %s ORDER BY "%s" DESC, id DESC
                                 """ %(keyvalue[0],keyvalue[1], keyvalue[2], keyvalue[3], self.schema,table, keyvalue[0], 'is NULL' if value == 'NULL' else " = '%s'" %value, keyvalue[2])
                        res = self.pgcon.run(sql, True)

                        if len(res) != 0: # if we have at least one price entry for this booliId
                            value = valueDic[table][keyvalue[1]]
                            skip = True

                            if value != 'NULL':
                                #print((valueDic[table][keyvalue[0]], valueDic[table][keyvalue[1]], valueDic[table][path]) in res)
                                #for r in res:
                                    #if [valueDic[table][keyvalue[0]], valueDic[table][keyvalue[1]], valueDic[table][path]]  ==

                                for r in res:
                                    #print(r, value)
                                    #print(r , datetime.datetime.strptime(valueDic[table][keyvalue[2]].split()[0],"%Y-%m-%d" ), value)

                                    # if this price appears earlier than price from priceHistory
                                    if r[3] > datetime.datetime.strptime(valueDic[table][keyvalue[2]].split()[0],"%Y-%m-%d" ):
                                        skip = True
                                        break

                                    # if price from priceHistory is None get next price
                                    if r[2] is None:
                                        continue
                                    else:
                                        #print (str(r[2]), str(valueDic[table][path]), str(r[2]) == valueDic[table][path] )
                                        # if this price equals to price from priceHistory
                                        if r[2] == value:
                                            c = valueDic[table][keyvalue[3]]
                                            curSoldPrice = True if c == 'True' else False

                                            #print(r[3], r[3] == curSoldPrice)

                                            if r[4] == curSoldPrice:
                                                skip = True
                                            else:
                                                skip = False
                                            break
                                        else:
                                            #print(r, res)
                                            #print(str(r[2]), str(valueDic[table][path]))
                                            skip = False
                                            break

                            if skip:
                                skipTable.append((table))

                        # if new entry for this booliId, apply it to the table


            #____FILL VALUES____________________________________________________________

            #print('ValueDic',valueDic)
            #print (self.primaryKeys)

            for table in valueDic:

                if table in skipTable:
                    continue

                for column in valueDic[table]:
                    if '%s.%s' % (table, column) in skipColumn:
                        continue

                    uoi = INSERT
                    #print (table, column)
                    if '%s.%s' %(table,column) in self.primaryKeys:
                        #print (table, column)
                        value = valueDic[table][column]

                        sql = """SELECT * FROM "%s"."%s" WHERE "%s" = '%s' """ % (self.schema, table, column, value)
                        res = self.pgcon.run(sql, True)
                        # if this pkey already exists in table, rewrite it
                        if len(res) != 0:
                            #print (res)
                            uoi = UPDATE
                            pkcol = column
                            pkval = value

                        break

                if uoi == UPDATE:
                    sql = """UPDATE "%s"."%s" SET""" %(self.schema,table)

                    for column in valueDic[table]:
                        value = valueDic[table][column]
                        sql += """ "%s" = %s,""" %(column, 'NULL' if value=='NULL' else "'%s'" %value)

                    sql = sql[:-1] + """ WHERE "%s" = '%s' """ %(pkcol, pkval)

                    #if table =='listings':
                     #   print(sql)

                elif uoi == INSERT:
                    sql = """INSERT INTO "%s"."%s" ( """ % (self.schema, table)

                    for column in valueDic[table]:

                        if '%s.%s' % (table, column) in skipColumn:
                            continue

                        sql += '"%s", ' % column

                    sql = sql[:-2] + ') VALUES ('

                    for column in valueDic[table]:
                        value = valueDic[table][column]

                        if '%s.%s' % (table, column) in skipColumn:
                            continue

                        sql += "%s," % ('NULL' if value == 'NULL' else "'%s'" % value)

                    sql = sql[:-1] + ')'

                res = self.pgcon.run(sql)

                #if valueDic['priceHistory']['booliId'] == '2098509':
                #print (sql)

                if res != 0:
                    return err("Error while inserting data into %s.%s\n%s" %(self.schema,table, valueDic[table]))

                self.updateTable(table, valueDic)


    #     Table specific rules which cannot be described by the rules
    def updateTable(self, table, valueDic):
        #print(valueDic['listings']['dateSold'])
        if table == 'listings':
            #print (valueDic['listings']['dateSold'])

            #   set isActive and dateinactive
            if valueDic['listings']['dateSold'] == 'NULL':
                sql = """UPDATE "%s"."%s" SET "isActive" = 'True', "dateInactive" = NULL
                          WHERE "booliId" = %s """ %(self.schema, table, valueDic['listings']['booliId'])
            else:
                sql = """UPDATE "%s"."%s" SET "isActive" = 'False', "dateInactive" = '%s'
                    WHERE "booliId" = %s """ % (self.schema, table, valueDic['listings']['dateSold'], valueDic['listings']['booliId'])
                #print('dateInactive:',self.date)
            self.pgcon.run(sql)



    def getDicValue(self,dic,s):
        l = s.split(':')

        if len(l) == 1:
            if s in dic:
                res = dic[s]

                if type(res) is list:
                    return ','.join(res)
                else:
                    return res
            else:
                return None
        else:
            if l[0] in dic:
                return self.getDicValue(dic[l[0]],':'.join(l[1:]))
            else:
                return None


    def checkKey(self, key):
        val = key
        specialKey = False

        if key == '_DATEFROMFILENAME_':
            specialKey = True
            fname = self.source.split('/')[-1]
            # print(fname)
            if fname[:5] == 'booli':
                val = fname.split()[1]

        if key == '_FALSE_':
            specialKey = True
            val = 'False'

        if key == '_TRUE_':
            specialKey = True
            val = 'True'

        return (val, specialKey)



    #   Get maximum update version from DBStruct configs

    def getMaxVersion(self, fdbstruct = None):
        if fdbstruct is None:
            fdbstruct = self.fdbstruct

        jsonData = open(fdbstruct).read()
        dbstruct = json.loads(jsonData)
        maxU = 0

        for u in dbstruct['UPDATES']:
            if int(u) > maxU:
                maxU = int(u)

        val = dbstruct['UPDATES'][str(maxU)]

        if type(val) is dict:
            return maxU
        elif type(val) is str:
            key,path = val.split('##')
            if key == 'FILE':
                return self.getMaxVersion(os.path.dirname(self.fdbstruct)+'/' + path)
            else:
                return maxU - 1
        else:
            return err('Unknown update method %s' %dbstruct['UPDATES'])


    #    Get db structure dictionary for given update version

    def getDBStruct(self, uversion, fdbstruct = None):
        if fdbstruct is None:
            fdbstruct = self.fdbstruct

        jsonData = open(fdbstruct).read()
        dbstruct = json.loads(jsonData)
        maxU = 0

        for u in dbstruct['UPDATES']:
            if int(u) == uversion and type(dbstruct['UPDATES'][u]) is dict:
                return dbstruct['UPDATES'][u]
            if int(u) > maxU:
                maxU = int(u)

        #print (type(dbstruct['UPDATES'][str(maxU)]))
        if type(dbstruct['UPDATES'][str(maxU)]) is str:
            key,path = dbstruct['UPDATES'][str(maxU)].split('##')
            if key == 'FILE':
                return self.getDBStruct(uversion, path)
        else:
            return err("Cannot find requested version")



    # ---------------   This is booli-specific function to prepare for data load ---------------

    def initFill(self):
        sql = """UPDATE  "%s"."%s" SET "isActive" = 'False', "dateInactive" = '%s' WHERE "dateSold" is NULL AND "dateInactive" is NULL """ %(self.schema, 'listings', self.date)
        self.pgcon.run(sql)




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
        self.options = self.handleParams(params)
        self.params = params.replace("-f", "").strip()
        self.username = username
        #
        #
        # self.transfer = False
        # self.downloadAction = None
        # self.updateVersion = None
        # self.recreate = False
        # self.mcommand = None
        # self.clean = False
        # self.latest = False
        # self.config = None


    def handleParams(self, params):
        options = {}
        #print("parametersp",params[0:2])
        if params.find('-f') != -1:
            options['force'] = True
        else:
            options['force'] = False

        if params[0:3] == '-d ':
            options['download'] = params[3:].split()[0]

            if params.find('-l') != -1:
                options['latest'] = True
            else:
                options['latest'] = False

        elif params[0:2] == '-u':
            options['upload'] = True
        elif params[0:2] == '-s':
            options['stop'] = True
        elif params[0:2] == '-a':
            options['analyze'] = True
        else:
            return None

        return options


    def run(self):
        if self.options is None:
            tolog(ERROR, "no known parameters were found: %s" % self.params)
            return 1

        #print(self.options)

        db_from_env = dj_database_url.config()
        db = DataBase(connection = pgUtil.pgProcess(database=db_from_env['NAME'],
                                                    host=db_from_env['HOST'],
                                                    user=db_from_env['USER'],
                                                    port=db_from_env['PORT'],
                                                    password=db_from_env['PASSWORD']), frules = gDBFillRules)

        today = datetime.date.today()
        today_scripts = Info.objects.filter(started__date = today)
        info = None
        runbefore = False

        if 'stop' not in self.options:
            for s in today_scripts:
                if s.config == self.params:
                    runbefore = True
                    if s.status == 'done' and not self.options['force']: # if succesfully run before
                        str = 'already run for %s' %self.params
                        tolog(INFO, str)
                        return 1
                    else:
                        s.status = 'started'
                        s.save()
                        info = s
                        break

            if not runbefore:
                l = Info(user_name = self.username,
                         config = self.params,
                         status = 'started')
                l.save()
                info = l
        # _________________________________________________________________________________________

        if 'download' in self.options:
            tolog(INFO, ("Downloading %s" %self.options['download']))

            a = Aux.objects.update_or_create(key = 'DownloadAuxKey', defaults={"key" : "DownloadAuxKey",
                                                                                "value" : "run"})
            #print(self.options['latest'])
            t = threading.Thread(target = self.getDataFromWeb, args = (info, self.options['latest']) )
            t.start()


        # -----------------------------------------------------------------------------------

        if 'stop' in self.options and self.options['stop']:
                a = Aux.objects.update_or_create(key='DownloadAuxKey', defaults={"key": "DownloadAuxKey",
                                                                             "value": "stop"})

        if 'upload' in self.options and self.options['upload']:
            tolog(INFO, 'Uploading data')
            t = threading.Thread(target = db.uploadData)
            t.start()


        return 0
        if self.transfer:
            logging.info("Uploading data")


            flist = os.listdir(BASE_FOLDER + '/data/')
            idx = 0

            while flist[idx][:5] != 'booli':
                idx += 1

            db.date = (datetime.datetime.strptime(flist[idx].split()[1], "%Y-%m-%d") - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
            #print(db.date)
            db.initFill()

            for idx, file in enumerate(flist):
                if file[:5] == 'booli':
                    # logging.info("Uploading file %s %s/%s" %(file,idx,len(flist)))
                    logging.info("Uploading file %s %s/%s" % (file, idx + 1, len(flist)))
                    db.fillDB(source=BASE_FOLDER + '/data/' + file)

        # -----------------------------------------------------------------------------------

        if self.clean:
            logging.info("Cleaning data folder")
            flist = os.listdir(BASE_FOLDER + '/data/')

            if flist is not None:
                for file in flist:
                    #print(file)
                    print(BASE_FOLDER + '/data/' + file, BASE_FOLDER + '/dataHistory/' + file)
                    shutil.copyfile('' + BASE_FOLDER + '/data/' + file + '', '' + BASE_FOLDER + '/dataHistory/' + file + '')
                    os.remove(BASE_FOLDER + '/data/' + file)

        if self.recreate:
            sql = sql = """INSERT INTO "%s".history values(%s,now(), '%s', 'DB created') """ %(db.schema, 1, self.options)
            res = db.pgcon.run(sql)
        elif not self.force:
            sql = """UPDATE "%s".history SET status = '%s done' WHERE id = %s""" %(db.schema, s, id + 1)
            res = db.pgcon.run(sql)

    def getDataFromWeb(self, info = None, latest = False):
        uniqueString = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        timestamp = str(int(time.time()))
        hashstr = sha1((gCallerId + timestamp + gUniqueKey + uniqueString).encode('utf-8')).hexdigest()
        urlBase = 'HTTP://api.booli.se//'

        if not (self.options['download'] == 'listings' or self.options['download'] == 'sold'):
            tolog(ERROR, ("Wrong type of download %s" %self.options['download']))
            return 1

        urlBase += '%s?' % self.options['download']
        area_list = ['64',  # Skane
                     # '160', #Halland
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
                    print('stop thread')
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

        aux = Aux.objects.get(key = 'DownloadAuxKey')
        aux.value = 'complete'
        aux.save()

        info.status = 'done'
        info.save()



# if __name__ == "__main__":
#     prog = svrea_script()
#     sys.exit(prog.run())