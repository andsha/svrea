fread = open('./static/maps/Sweden/Muni.kml', 'r')
fwrite = open('./static/maps/Sweden/Muni_reduced.kml', 'w+')
i = 0
while True:
    l = fread.readline()
    i += 1

    if not l:
        break

    if '<Style' in l:
        while True:
            l = fread.readline()
            if '<Placemark>' in l:
                break

    if '<Polygon>' in l:
        #print('started %s' %i)
        bigl = ''
        writeinf = True

        while True:
            l = fread.readline()
            i += 1

            if '<innerBoundaryIs>' in l:
                while True:
                    l = fread.readline()
                    if '</innerBoundaryIs>' in l:
                        l = fread.readline()
                        break

            if '</Polygon>' in l:
                #print('stopped %s, %s' % (i, writeinf) )
                if writeinf:
                    fwrite.write('<Polygon>\n%s</Polygon>' %bigl)
                break

            if '<coordinates>' in l:
                coords = fread.readline().strip().split(' ')
                i += 1

                l = ''
                if len(coords) > 50:
                    t = 0
                    l1_old = coords[0].split(',')[0][0:5]
                    l2_old = coords[0].split(',')[0][0:5]
                    for c in coords:
                        #print('c=%s' %c)
                        l1 = c.split(',')[0][0:5]
                        l2 = c.split(',')[1][0:5]
                        if l1 != l1_old and l2 != l2_old:
                            nl = '%s,%s,%s' %(l1, l2, 0)
                            l = '%s %s' %(l, nl)
                            l1_old = l1
                            l2_old = l2
                            t += 1
                    if t < 5:
                        #print(i)
                        writeinf = False
                else:
                    #print('small area %s' % (i))
                    writeinf = False

                l = '<coordinates>\n%s\n' %l
            bigl = '%s%s' %(bigl, l)
    else:
        fwrite.write(l)

fread.close()
fwrite.close()









#select count(*) from svrea_script_listings l join svrea_script_address a on l.address_id = a.addressid where a.municipality='Stockholm' and datesold::date='2017-05-14'
#select sum(l.latestprice)/count(*)  from svrea_script_listings l join svrea_script_address a on l.address_id = a.addressid where l.datesold='2017-05-26' and a.county='Skåne län';