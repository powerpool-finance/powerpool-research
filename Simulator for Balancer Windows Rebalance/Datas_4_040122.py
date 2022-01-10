#!/usr/bin/env python
# coding: utf-8

# In[12]:


#Balancer V2 Pool AAVE, SNX, SUSHI, YFI
import csv
import sys
sys.path.append('../datas')

with open("./BINANCE_AAVEUSDT_1.csv", encoding='utf-8') as r_file:
    file_reader = csv.reader(r_file, delimiter = ",")
    counter=0
    aave=[]
    for row in file_reader:
        if counter==0:
            counter = 1
        else:
            aave.append([row[0], float(row[1]), float(row[2]),float(row[3]),float(row[4])])#time,open,close, volume\n",
#print (aave)\n",
with open("./BINANCE_SNXUSDT_1.csv", encoding='utf-8') as r_file:
    file_reader = csv.reader(r_file, delimiter = ",")
    counter=0
    snx=[]
    for row in file_reader:
        if counter==0:
             counter = 1
        else:
            snx.append([row[0], float(row[1]), float(row[2]),float(row[3]), float(row[4])])#time,open,close, volume\n",
#print (snx)
with open("./BINANCE_YFIUSDT_1.csv", encoding='utf-8') as r_file:
    file_reader = csv.reader(r_file, delimiter = ",")
    counter=0
    yfi=[]
    for row in file_reader:
        if counter==0:
             counter = 1
        else:
            yfi.append([row[0], float(row[1]), float(row[2]),float(row[3]), float(row[4])])#time,open,close, volume\n",
#print (yfi)
with open("./BINANCE_SUSHIUSDT_1.csv", encoding='utf-8') as r_file:
    file_reader = csv.reader(r_file, delimiter = ",")
    counter=0
    sushi=[]
    for row in file_reader:
        if counter==0:
                #print(row[0], row[4], row[15])
               # print(' ')
            counter = 1
        else:
            sushi.append([row[0],float(row[1]), float(row[2]),float(row[3]), float(row[4])])#time,open,high,low,close,, volume\n",
#print (aave)\n",
#print(aave[0][3], sushi[0][0], yfi[0][0], snx[0][0])# check the start time\n",

datas=[]#time, price aave, price sushi, price yfi, price snx, volume aave, volume sushi, volume yfi, volume snx
for i in range(0, len(aave), 1):
    datas.append([aave[i][4], sushi[i][4],snx[i][4], yfi[i][4], aave[i][0] ])


# In[15]:


#print(aave[-1], sushi[-1], snx[-1], yfi[-1])
#datas[-1]


# In[17]:


#print(datas)


# In[ ]:





# In[ ]:




