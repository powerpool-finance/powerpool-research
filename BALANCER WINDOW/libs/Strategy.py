#!/usr/bin/env python
# coding: utf-8

# ## Functions of three Strategies

# In[ ]:
from Balancer_lib_new import *
fee=0.3

# In[ ]:
def strategy1(pool1, ratio1, datas, n, step):
    st=[]

    arr_pool1=[]
    arr_value_pool1=[]
    arr_value_tokens1=[]
    arr_IL1=[]
    w1=[]
    arr_ratio1=[]

    #Strategy1 - datas
    for step in range(0, len(datas)):
        st.append(step)
        datas.append(datas[step])
        pool11 = pool_from_ratio_oldpool(pool1, ratio1, datas, step,  n)
        weights11 = weights_from_new_pool(pool11, datas, step, n)
        w1.append(weights11)
    
        value01=value(pool1, datas, step, n)#before swap
        sw1 = swaps_new1(pool1, weights11, datas, step, n, value01, fee)
        pool11 =sw1[0]
        arr_pool1.append(pool11)
        v1=value_tokens(pool11, datas, step, n)
        arr_value_tokens1.append(v1)
        rt11=ratio_tokens(pool11, datas, step, n)
        arr_ratio1.append(rt11)
        value1=value(pool11, datas, step, n)#after swap
    
        arr_value_pool1.append(value1)
        IL1=(value1-value01)/value01
        arr_IL1.append(IL1)
    return arr_IL1, arr_ratio1


# In[ ]:


def strategy2(pool2, weights2, ratio1, datas, step, n, fee, start_step, n_steps):
    pool2_end = pool_from_ratio_oldpool(pool2, ratio1, datas, start_step,  n)
    weights_end = weights_from_new_pool(pool2_end, datas, start_step, n)
    dif_weights = [0]*n
    for i in range(0,n):
        dif_weights[i] = (weights_end[i] - weights2[i])/(n_steps)
    st2=[]
    arr_pool2=[]
    arr_value_tokens2=[]
    arr_value_pool2=[]
    arr_IL2=[]
    w2=[]
    arr_ratio2=[]
    arr_tot_IL2=[]
    IL2_tot=0
    for step in range(start_step, start_step+n_steps+1):
        st2.append(step)
        value02=value(pool2, datas, step, n)#before swap
        for i in range(0, n):
            weights2[i]+=dif_weights[i]
         
        
        
        sw2 = swaps_new1(pool2, weights2, datas, step, n, value02, fee)
        pool2 =sw2[0]
    
        #w2.append(weights2)
        #arr_pool2.append(pool2)
        v2=value_tokens(pool2, datas, step, n)
        arr_value_tokens2.append(v2)
        rt2=ratio_tokens(pool2, datas, step, n)
        arr_ratio2.append(rt2)
        value2=value(pool2, datas, step, n)#after swap
    
        arr_value_pool2.append(value2)
        IL2=(value2-value02)/value02
        arr_IL2.append(IL2)
        IL2_tot+=IL2
        arr_tot_IL2.append(IL2_tot)    
        
    return arr_tot_IL2, rt2


# In[ ]:


import copy
def descr_ratio(ratio):#ratio - array
    rat = copy.deepcopy(ratio)
    r=[]
    place=[-1]*len(ratio)
    r=sorted(ratio, reverse=True)
    for i in range(0,len(ratio)):
        for j in range(0,len(ratio)):
            if r[i]==rat[j]:
                #print('i= ',i,' j = ',j,r[i],rat[j])
                place[i]=j
                rat[j]=5
                break
        
    return r, place


# In[ ]:


def strategy3(pool3, weights3, ratio1, datas, step, n, fee, start_step, n_steps, vel):
    st3=[]
    arr_pool3=[]
    arr_value_tokens3=[]
    arr_value_pool3=[]
    arr_IL3=[]
    w3=[]
    arr_ratio3=[]
    arr_tot_IL3=[]
    IL3_tot=0
#print(pool3)
    for step in range(start_step, start_step+n_steps+1):
        counter=0
        st3.append(step)
        value03=value(pool3, datas, step, n)#before swap
        delta_price = delta_spot_market_procent(pool3, weights3, datas, step, n, value03)
    
        #if start_step<=step and step<=start:
        current_ratio = ratio_tokens(pool3, datas, step, n)
        r1=descr_ratio(ratio1)[0]
        pr1=descr_ratio(ratio1)[1]
        cr=descr_ratio(current_ratio)[0]
        pcr=descr_ratio(current_ratio)[1]
        
        if r1[0]>cr[0] and  r1[n-1]<cr[n-1] :
            
            if delta_price[pr1[0]]>0  and delta_price[pr1[n-1]]<0:
                pool3_end = pool_from_ratio_oldpool(pool3, ratio1, datas, step,  n)
                w3=weights_from_new_pool(pool3_end, datas, step, n)
                for i in range(0, n):
                    weights3[i]+=(w3[i]-weights3[i])/vel
        else:
            w3=weights_from_new_pool(pool3, datas, step, n)
            for i in range(0, n):
                weights3[i]+=(w3[i]-weights3[i])/vel
        sw3 = swaps_new1(pool3, weights3, datas, step, n, value03, fee)
        pool3 =sw3[0]

        w3.append(weights3)

        arr_pool3.append(pool3)
        v3=value_tokens(pool3, datas, step, n)
        arr_value_tokens3.append(v3)
        rt3=ratio_tokens(pool3, datas, step, n)
        arr_ratio3.append(rt3)

        value3=value(pool3, datas, step, n)#after swap

        arr_value_pool3.append(value3)
        IL3=(value3-value03)/value03
        arr_IL3.append(IL3)
        IL3_tot+=IL3
        arr_tot_IL3.append(IL3_tot)
    
    return arr_tot_IL3, arr_ratio3

print('Import Datas for Strategies finished.')

