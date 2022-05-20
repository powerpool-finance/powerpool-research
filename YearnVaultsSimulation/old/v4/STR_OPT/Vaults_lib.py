#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import plotly
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from decimal import Decimal
import datetime
import pprint
import csv


# In[ ]:


# This function computes the difference in Share Price for every Vault for Current Moment vs Some time ago
# The difference in Share Price is efficiently the profit earned in Vault during this period
def calc_price_velosity(n, price, i, delta):
    arr=[]
    if (i+delta)<=(len(price)-1):
        for j in range (1, n+1, 1):
            #de=(float(price[i+delta][j])-float(price[i][j]))/delta
            de=(float(price[i][j])-float(price[i-delta][j]))/delta
            if de<0:
                de=0
            arr.append(de)
    else:
        print ('calc_price_velosity: ERROR :i+delta > max datas')
    return arr
#------
# This function computes the difference in TVL for every Vault for Current Moment vs Some time ago

def calc_tvl_velosity(n, tvl, i, delta):
    arr=[]
    if (i+delta)<=(len(tvl)-1):
        for j in range (1, n+1, 1):
            de=(float(tvl[i+delta][j])-float(tvl[i][j]))/delta
            if de<0:
                de=0
            arr.append(de)
    else:
        print ('calc_tvl_velosity: ERROR :i+delta > max datas')
    return arr  
#----------------------------------
# This function computes shares of Vaults inside the basket if the are rebalanced based purely on TVL approach
# It means that each Vault will have a share = TVL_in_this_Vault / sum_i(TVL_i)

def calc_shares_tvl(n, tvl, i, total_funds, delta, param):
    totalTVL=0
    sum1=0
    funds=[param/n*total_funds]*n
    if (i+delta)<=(len(tvl)-1):
        for j in range (1, n+1, 1):
            totalTVL=totalTVL+tvl[i][j]
        
        for j in range (0, n, 1):
            funds[j]=funds[j]+(1-param)*total_funds*float(tvl[i][j+1])/totalTVL
            sum1=sum1+funds[j]
    else:
        print ('calc_shares_tvl: ERROR :i+delta > max datas')
    #print(sum1)
    d = total_funds - sum1    
    if d>0:
        funds[j]=funds[j]+d/n
    return funds
#--------
def calc_shares_tvl_velosity(n, tvl, i, total_funds, delta, param):#computing shares according TVL gain speed
    funds=[param/n*total_funds]*n
    speedTVL=calc_tvl_velosity(n, tvl, i, delta)#array
    #print('speedTVL=',speedTVL)
    tot_speed=0
    for j in range(0, n):
        tot_speed=tot_speed+speedTVL[j]
        tot_speed_abs=tot_speed+abs(speedTVL[j])
    #print('tot_speed=',tot_speed)
    
    if tot_speed>0:
        for j in range(0, n):    
            if speedTVL[j]>=0:
                funds[j]=funds[j]+(1-param)*total_funds*speedTVL[j]/tot_speed_abs
                #print('funds[j]', j, funds[j])
                
            else:
                funds[j]=0
        for j in range(0, n): 
            total_funds=total_funds-funds[j]
        #print('total_funds11', total_funds)
        while total_funds>1:
            #print('total_funds2', total_funds)
            for j in range(0, n):
                if funds[j]>0:
                    funds[j]=funds[j]+total_funds*0.1
                    total_funds=total_funds*0.9
    else:
        #print('All Vaults loss deposits ')
        for j in range(0, n):    
            funds[j]=total_funds/n
    return funds
#-------
def calc_shares_price_velosity(n, price, step, total_funds, delta, param):#computing shares according velosity of gain of vault prices
    #print('total_funds= ', total_funds)
    funds=[param/n*total_funds]*n
    total_velosity=0
    sum1=(1-param)/n*total_funds
    arr1=calc_price_velosity(n, price, step, delta)
    f=0
    
    for j in range(0, n):
        total_velosity = total_velosity+arr1[j]
    if total_velosity>0:
        for j in range(0, n):
            funds[j] =funds[j]+(1-param)*total_funds*arr1[j]/total_velosity
    else:
        for j in range(0, n):
            funds[j] =funds[j]+(1-param)*total_funds/n
            
    return funds
#print('Strategy 3 - price velosity')
#print('calc_shares_price_velosity = ',calc_shares_price_velosity(n, price, 9, total_funds, 3))
#-----------------
def frange(start, end, step):
    i = start
    while i < end:
        yield i
        i += step
#-------
#--calculate Profit from investing if known the volume of money  in each Vault (FUNDS) for Z-th step for DELTA steps---------------
def calc_profit_step(n,price, funds, step, delta):
    prof=0
    i=step
    for j in range(0,n,1):
        prof = prof+funds[j]*(float(price[i+delta][j+1])-float(price[i][j+1]))
    return prof

#Testing Calc_profit_step for ONE Basket Adjustment

#print('profit for this ', delta,' steps = ', calc_profit_step(n,price, funds, 1, delta)) # for check
#--------------

#--calculate Profit from investing for period/ If period = 0, then calculate for all datas
def calc_profit_for_period(n, price, funds, delta,start_step, period):
    prof=0
    if (period>0) and (period< len(price)):
        delta1=period
        prof = prof+calc_profit_step(n,price, funds, start_step, delta1)
    
    return prof
#-----------------------

