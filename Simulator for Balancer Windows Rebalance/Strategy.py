#!/usr/bin/env python
# coding: utf-8

# ## Functions of three Strategies

# In[ ]:
from Balancer_lib_new import *
fee=0.3
import copy

# In[ ]:
def strategy1(pool1, ratio1, datas, n, step, fee, gas_fee):
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
    return arr_IL1, arr_ratio1, pool11, w1


# In[ ]:


def strategy2(pool2, weights2, ratio1, datas, step, n, fee, start_step, n_steps, gas_fee):
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
    weights22=copy.deepcopy(weights2)
    for step in range(start_step, start_step+n_steps+1):
        st2.append(step)
        value02=value(pool2, datas, step, n)#before swap
        for i in range(0, n):
            weights22[i]+=dif_weights[i]
         
        
        
        sw2 = swaps_new1(pool2, weights22, datas, step, n, value02, fee)
        pool2 =sw2[0]
    
        w2.append(weights22)
        arr_pool2.append(pool2)
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
        
    return arr_tot_IL2, rt2, pool22, w2


# In[ ]:



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


def strategy3(pool3, weights3, ratio1, datas, step, n, fee, start_step, n_steps, vel, gas_fee):
    pool3_end = pool_from_ratio_oldpool(pool3, ratio1, datas, start_step,  n)
    weights_end = weights_from_new_pool(pool3_end, datas, start_step, n)
    dif_weights = [0]*n
    #print('weights old, new = ',weights3,weights_end )
    for i in range(0,n):
        dif_weights[i] = (weights_end[i] - weights3[i])/(vel)
    
    st3=[]
    arr_pool3=[]
    arr_value_tokens3=[]
    arr_value_pool3=[]
    arr_IL3=[]
    w3=[]
    arr_ratio3=[]
    arr_tot_IL3=[]
    IL3_tot=0
    weights33=copy.deepcopy(weights3)
    for step in range(start_step, start_step+n_steps+1):
        counter=0
        st3.append(step)
        value03=value(pool3, datas, step, n)#before swap
        delta_price = delta_spot_market_procent(pool3, weights33, datas, step, n, value03)
    
        #if start_step<=step and step<=start:
        current_ratio = ratio_tokens(pool3, datas, step, n)
        r1=descr_ratio(ratio1)[0]
        pr1=descr_ratio(ratio1)[1]
        cr=descr_ratio(current_ratio)[0]
        pcr=descr_ratio(current_ratio)[1]
        
        if r1[0]>cr[0] and  r1[n-1]<cr[n-1] :
            
            if delta_price[pr1[0]]>0  and delta_price[pr1[n-1]]<0:
                for i in range(0, n):
                    weights33[i]+=dif_weights[i]
                sw3 = swaps_new1(pool3, weights33, datas, step, n, value03, fee)
                pool3 =sw3[0]
        else:
            #print('stop !!!')
            break
        w3.append(weights33)

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
    
    return arr_tot_IL3, arr_ratio3, pool3, w3

print('Import Datas for Strategies finished.')

# In[6]:


def strategy1_1_step(pool1, ratio1, datas, n, step, fee, gas_fee):
    arr_pool1=[]
    arr_value_pool1=[]
    arr_value_tokens1=[]
    arr_IL1=[]
    #w1=[]
    arr_ratio1=[]

    pool11 = pool_from_ratio_oldpool(pool1, ratio1, datas, step,  n)
    weights11 = weights_from_new_pool(pool11, datas, step, n)
       
    
    value01=value(pool1, datas, step, n)#before swap
    #sw1 = swaps_new1(pool1, weights11, datas, step, n, value01, fee)
    sw1 = swaps_gas_fee(pool1, weights11, datas, step, n, value01, fee, gas_fee)
    pool11 =sw1[0]
    #arr_pool1.append(pool11)
    v1=value_tokens(pool11, datas, step, n)
    #arr_value_tokens1.append(v1)
    rt11=ratio_tokens(pool11, datas, step, n)
    #arr_ratio1.append(rt11)
    value1=value(pool11, datas, step, n)#after swap
    #arr_value_pool1.append(value1)
    IL1=(value1-value01)/value01
    #arr_IL1.append(IL1)
    return IL1, rt11, pool11, weights11, v1# return Impermanent loss, ration of tokens, new pool, new weights, value of tokens


# In[7]:


def strategy2_1_step(pool2, weights2, ratio1, datas, start_step, n, fee, n_steps, gas_fee):
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
    weights22=copy.deepcopy(weights2)
    for step in range(start_step, start_step+n_steps):
        st2.append(step)
        value02=value(pool2, datas, step, n)#before swap
        for i in range(0, n):
            weights22[i]+=dif_weights[i]
          
        
        #sw2 = swaps_new1(pool2, weights2, datas, step, n, value02, fee)
        sw2 = swaps_gas_fee(pool2, weights22, datas, step, n, value02, fee, gas_fee)
        pool2 =sw2[0]
    
        w2.append(weights22)
        arr_pool2.append(pool2)
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
        #if 
        
    return arr_tot_IL2, arr_ratio2, pool2, w2, arr_value_tokens2
    # return Impermanent loss, ration of tokens, new pool, new weights, value of tokens


# In[8]:


def strategy3_1_step(pool3, weights3, ratio1, datas, start_step, n, fee,  n_steps, vel, gas_fee):
    pool3_end = pool_from_ratio_oldpool(pool3, ratio1, datas, start_step,  n)
    weights_end = weights_from_new_pool(pool3_end, datas, start_step, n)
    dif_weights = [0]*n
    #print('weights old, new = ',weights3,weights_end )
    for i in range(0,n):
        dif_weights[i] = (weights_end[i] - weights3[i])/(vel)
    #print('dif_weights= ', dif_weights)
        
    st3=[]
    arr_pool3=[]
    arr_value_tokens3=[]
    arr_value_pool3=[]
    arr_IL3=[]
    w3=[]
    arr_ratio3=[]
    arr_tot_IL3=[]
    IL3_tot=0
    weights33=copy.deepcopy(weights3)
    for step in range(start_step, start_step+n_steps):
        #counter=0
        st3.append(step)
        value03=value(pool3, datas, step, n)#before swap
        
        
        delta_price = delta_spot_market_procent(pool3, weights33, datas, step, n, value03)
    
        
        current_ratio = ratio_tokens(pool3, datas, step, n)
        r1=descr_ratio(ratio1)[0]
        pr1=descr_ratio(ratio1)[1]
        cr=descr_ratio(current_ratio)[0]
        pcr=descr_ratio(current_ratio)[1]
        #print(step,r1[0],cr[0], r1[n-1],cr[n-1])
        
        if r1[0]>cr[0] and  r1[n-1]<cr[n-1] :
            #print('Меняем веса')
            for i in range(0, n):
                    weights33[i]+=dif_weights[i]
                    
            if delta_price[pr1[0]]>0  and delta_price[pr1[n-1]]<0:
                #print('Торгуем')
                
                #sw3 = swaps_new1(pool3, weights3, datas, step, n, value03, fee)
                sw3 = swaps_gas_fee(pool3, weights33, datas, step, n, value03, fee, gas_fee)
                #print('результат торгов = ',sw3)
                pool3 =sw3[0] 
        else:
            #print('stop !!!')
            break
        #sw3 = swaps_new1(pool3, weights33, datas, step, n, value03, fee)
        #pool3 =sw3[0]
        w3.append(weights33)

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
    
    return arr_tot_IL3, arr_ratio3, pool3, w3, arr_value_tokens3


# In[9]:


print('Imported Strategies 1 Start Step')


# In[ ]:
