
import os
from manage import DEFAULT_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
import django
import datetime


def job():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    weekago = datetime.date.today() - datetime.timedelta(days=7)
    django.setup()
    from script.svrea_script import area_list, Svrea_script, tolog, INFO
    alist = [x[0] for x in area_list]
    uname = 'dailyjob'
    #********************************************************************
    tolog(INFO, 'start job')
    params = {'download': 'sold',
              'downloadLast': True,
              'forced': False,
              'area': alist}
    script = Svrea_script(params=params, username=uname)
    try:
        script.run()
    except Exception as e:
        tolog(INFO, e)
    # ********************************************************************
    params = {'download': 'listings',
              'downloadLast': False,
              'forced': False,
              'area': alist}
    script = Svrea_script(params=params, username=uname)
    try:
        script.run()
    except Exception as e:
        tolog(INFO, e)
    # ********************************************************************
    params = {'upload': True,
              'forced': True}
    script = Svrea_script(params=params, username=uname)
    try:
        script.run()
    except Exception as e:
        tolog(INFO, e)
    #********************************************************************
    # period ETL
    for p in ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']:
        params = {'analyze': True,
                  'etlRange': '%s:%s' %(weekago.strftime('%Y-%m-%d'),
                                        yesterday.strftime('%Y-%m-%d')),
                  'etlPeriodType': p,
                  'numThreads' : '1'
                  }
        script = Svrea_script(params=params, username=uname)
        try:
            script.run()
        except Exception as e:
            tolog(INFO, e)


    tolog(INFO, 'finish daily job')
