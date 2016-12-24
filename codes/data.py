import time
import sys
import math
import random
import csv
from itertools import izip
from matplotlib import pyplot as plt
import numpy as np

filename = 'routes_24days_100pedestrains.csv'
time = []
uniquetime = []
femto = []
days=[]
count = {}
with open(filename,'r') as dest_f:
        data_iter = csv.DictReader(dest_f, delimiter = ',')
        headers = data_iter.fieldnames
        for row in data_iter:
            time.append(int(row['Minutes']))
            femto.append(int(row['FemtoCell']))
            days.append(int(row['Day']))
            
#time.sort()
uniquetime = list(set(time))
uniquetime.sort()
days.sort()

countwithday = {}
uniquedays = list(set(days))
print uniquedays

for d in uniquedays:
    time1 = time[(d-1)*28800:d*28800]
    femto1 = femto[(d-1)*28800:d*28800]
    for i in range (len(time1)):
        j = time1[i]
        if j not in count.keys():
            count[j] = {}
            k = femto1[i]
            if k not in count[j]:
                count[j][k] = 1

        else:
            k = femto1[i]
            if k not in count[j]:
                count[j][k] = 1
            else:
                count[j][k] = count[j][k] + 1
    countwithday[d] = count
    count = {}

#print countwithday

uniquetime = list(set(time))
femtocell = 1
uniquetime.sort()
usercount = []

out = open('femtodata_24d_100p.csv','wb')
writer = csv.writer(out, delimiter=',')
data = [['F1','F2','F3','F4','F5','F6','F7','F8','F9']]
writer.writerows(data)
alldata = []
daydata = []
for d in uniquedays:
    print d
    count = countwithday[d]
    alldata=[]
    femtocell = 1
    while femtocell <10:
        usercount = []
        for i in uniquetime:
            j = count[i]
            flag = False
            #print j
            #usercount.append(i)
            
            for k in j.keys():
                if k == femtocell:
                    flag=True
                    usercount.append(j[k])
            if flag==False:
                usercount.append(0)
        femtocell += 1
        alldata.append(usercount)
        #plt.scatter(uniquetime,usercount)
        #plt.show()
    
    daydata.append(alldata)
#print usercount

for i in daydata:
    writer.writerows(zip(*i))

print len(uniquetime)
print len(usercount)

