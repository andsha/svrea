from script.svrea_script import area_list, Svrea_script


def job():
    alist = [x[0] for x in area_list]
    uname = 'dailyjob'
    #********************************************************************
    params = {'download': 'sold',
              'downloadLast': True,
              'forced': False,
              'area': alist}
    script = Svrea_script(params=params, username=uname)
    script.run()
    # ********************************************************************
    params = {'download': 'listings',
              'downloadLast': False,
              'forced': False,
              'area': alist}
    script = Svrea_script(params=params, username=uname)
    script.run()
    # ********************************************************************
    params = {'upload': True,
              'forced': True}
    script = Svrea_script(params=params, username=uname)
    script.run()