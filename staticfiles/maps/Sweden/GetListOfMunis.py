flist = open('ListOfMunis.py', 'w+')
fmunis = open('Muni_reduced.kml', 'r')
listodmunis = []

for l in fmunis:
    if '<name>' in l:
        listodmunis.append(l.strip()[6:-7])

flist.write('MuniList = [')
for m in listodmunis[1:]:
    flist.write("'%s',\n" %m)
flist.write(']')

flist.close()
fmunis.close()