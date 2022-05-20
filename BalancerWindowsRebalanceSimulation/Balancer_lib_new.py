#!/usr/bin/env python
# coding: utf-8

# In[1]:


# define functions for prices
import numpy as np
def constanta (pool, weights, n):
    k=1
    for i in range(0,n,1):
        k=k*(pool[i]**weights[i])
    return k

#----------------
# value of pool
def value(pool, datas, step, n):
    v=0
    for i in range(0,n,1):
        v=v+pool[i]*datas[step][i]
        #print(v)
    return v

#-----------------
def pool_for_spot_usd(pool, value0, n):
    pool_1 =[0]*n
    for i in range(0,n,1):
        pool_1[i]=pool[i]
    pool_1.append(value0/n)
    return pool_1

#-----------------
#calc price in USD in moment = step
def market_price_usd(datas, step, n):
    pr=[0]*n
    for i in range(0,n,1):
        pr[i]=datas[step][i]
    return pr
#------------------

def spot_price_usd(pool, weights, datas, step, n, value0):
    pr=[0]*n
    usd_cost=pool_for_spot_usd(pool, value0, n)[n]
    for i in range(0,n,1):
        pr[i]=usd_cost*weights[i]/pool[i]/(1/n)
            
    return pr

#-------------------
#Computer the price difference between spot and market prices
def delta_spot_market_usd(pool, weights, datas, step, n, value0):
    d=[0]*n
    sp=spot_price_usd(pool, weights, datas, step, n, value0)
    #print('sp = ', sp)
    mp=market_price_usd(datas, step, n)
    #print('mp = ', mp)
    for i in range(0,n,1):
        d[i]=sp[i]-mp[i]
    return d
#-----------------
def delta_spot_market_procent(pool, weights, datas, step, n, value0):
    d=[0]*n
    sp=spot_price_usd(pool, weights, datas, step, n, value0)
    #print('sp = ', sp)
    mp=market_price_usd(datas, step, n)
    #print('mp = ', mp)
    for i in range(0,n,1):
        d[i]=(sp[i]-mp[i])/mp[i]
    return d
#-----------------


# In[2]:


#Functiouns for calculation swaps
def calc_out_given_in(pool, weights, fee, amount_in, dir_in, dir_out, n):# dir_in, amount_in, dir_out, amount_out 
    
    k=constanta (pool, weights, n) 
    totalfee=[0]*n
    a1=5
    a2=5
    for i in range(0,n,1):
        if (i!=int(dir_in)) and (i!=int(dir_out)):
            if a1!=5 and a2==5:
                a2=i
            if a1==5:
                a1=i
    amount_out=pool[dir_out] - (k/((pool[dir_in]+amount_in*(1-fee))**weights[dir_in])/(pool[a1]**weights[a1])/(pool[a2]**weights[a2]))**(1/weights[dir_out])
    return [  dir_in, amount_in, dir_out, amount_out ]# dir_in, amount_in, dir_out, amount_out 
#------------------------------
#calc direction for arbitrage trade
def calc_one_dir(pool, weights, datas, step, n, value0):
    d=delta_spot_market_procent(pool, weights, datas, step, n, value0)
    arr=d
    arr=sorted(arr, reverse = True)
    
    pos=[-1, -1]
    for i in range (0,n,1):
        if arr[0] == d[i]:
                pos[0]=i
        if arr[n-1] == d[i]:
                pos[1]=i
    return [pos[0], pos[1]]
#----------------------
#calc profit of arbitrager
def arbitr_profit_new(pool, weights, datas, step, n, value0, amount_in, fee):
    dir1 = calc_one_dir(pool, weights, datas, step, n, value0)
    dir_in=dir1[0]
    dir_out=dir1[1]
    amount_out = calc_out_given_in(pool, weights, fee, amount_in, dir_in, dir_out, n)[3]
    profit = amount_out*datas[step][dir_out]-amount_in*datas[step][dir_in]
    return profit
#--------------------------
#calc volume for  arbitrager trade with maximum profit 
def calc_amount_one_dir_new(pool, weights, datas, step, n,value0, fee):
    am_in=0
    am_out=0
    dir1 = calc_one_dir(pool, weights, datas, step, n, value0)
    dir_in=dir1[0]
    dir_out=dir1[1]
    start = pool[dir_in]/100
    end=pool[dir_in]
    ministep = pool[dir_in]/100
    profit1=0
    
    for i in np.arange (start, end, ministep ):
        amount_in = i
        pr = arbitr_profit_new(pool, weights, datas, step, n, value0, amount_in, fee)
        #print('pr = ', pr)
        if profit1<pr:
            profit1=pr
            am_in=amount_in
            am_out=calc_out_given_in(pool, weights, fee, amount_in, dir_in, dir_out, n)[3]
    return [dir_in, am_in, dir_out, am_out, profit1]
#------------------
#function for swap
import copy

def swap(pool, swap_plan):
    pool1 = copy.deepcopy(pool)
    pool1[swap_plan[0]]+=swap_plan[1]
    pool1[swap_plan[2]]-=swap_plan[3]
    return pool1
#----------------------
#function for many swaps per step if they are profitable for arbitrager
def swaps_new(pool, weights, datas, step, n, value0, fee):
    pool1 = copy.deepcopy(pool)
    
    arbitr_profit=0
    for i in range(0,n):
        swap_plan=calc_amount_one_dir_new(pool1, weights, datas, step, n, value0, fee)
        if swap_plan[4]>0:
            pool1 = swap(pool1, swap_plan)
            arbitr_profit+=swap_plan[4]
    return [pool1, arbitr_profit]


# In[3]:


def pool_from_amount(datas, step, n, amount):
    pool = [0]*n
    for i in range(0,n):
        pool[i]=amount/datas[step][i]
    return pool
    
def pool_from_token_values(datas, step, n, token_values):
    pool = [0]*n
    for i in range(0,n):
        pool[i]=token_values[i]/datas[step][i]
    return pool

# functions for calculate new pools from new ratio
#calc new pool from given new ratio and value of old pool

def pool_from_ratio_value(ratio, datas, step, value, n):# ratio = [], datas, step,total value of pool,
    arr=[0]*n
    for i in range(0,n,1):
        arr[i]=value*ratio[i]/datas[step][i]
    return arr

#----------------------
#calc new pool from old pool and new ratio
def pool_from_ratio_oldpool(pool, ratio, datas, step,  n):
    val= value(pool, datas, step, n)
    arr=pool_from_ratio_value(ratio, datas, step, val, n)
    return arr
#---------------
#print(pool_from_amount(datas, step, n, amount))
#print(pool_from_token_values(datas, step, n, token_values))
#------------------
def spot_price_usd_new(pool, weights, datas, step, n):# не нужна
    value0 = value(pool, datas, step, n)
    pr=[0]*n
    usd_cost=pool_for_spot_usd(pool, value0, n)[n]
    for i in range(0,n,1):
        pr[i]=usd_cost*weights[i]/pool[i]/(1/n)
    return pr
#-----------------
#calc weights for new pool and market prices
def weights_from_new_pool(pool, datas, step, n):
    w=[0]*n
    value1 = value(pool, datas, step, n)/n
    for i in range (0, n):
        w[i]=datas[step][i]*(1/n)*pool[i]/value1
    return w
#--------------------------
def value_tokens(pool, datas, step, n):
    v=[0]*n
    for i in range(0,n):
        v[i]=datas[step][i]*pool[i]
    return v #array
#------------------
def ratio_tokens(pool, datas, step, n):#for check result of destination desirable ratio
    r=[0]*n
    val0=value(pool, datas, step, n)
    for i in range(0,n):
        r[i]=datas[step][i]*pool[i]/val0
    return r #array
#----------------
def swaps_new1(pool, weights, datas, step, n, value0, fee):
    pool1 = copy.deepcopy(pool)
    
    arbitr_profit=0
    for i in range(0,n):
        swap_plan=calc_amount_one_dir_new(pool1, weights, datas, step, n, value0, fee)
        while swap_plan[4]>0:
            pool1 = swap(pool1, swap_plan)
            arbitr_profit+=swap_plan[4]
            swap_plan=calc_amount_one_dir_new(pool1, weights, datas, step, n, value0, fee)
    return [pool1, arbitr_profit]


# In[ ]:

def swaps_gas_fee(pool, weights, datas, step, n, value0, fee, gas_fee):
    pool1 = copy.deepcopy(pool)
    
    arbitr_profit=0
    for i in range(0,n):
        swap_plan=calc_amount_one_dir_new(pool1, weights, datas, step, n, value0, fee)#return [dir_in, am_in, dir_out, am_out, profit1]
        while swap_plan[4]>=2*gas_fee:
            pool1 = swap(pool1, swap_plan)
            arbitr_profit+=swap_plan[4]
            swap_plan=calc_amount_one_dir_new(pool1, weights, datas, step, n, value0, fee)
    return [pool1, arbitr_profit]



