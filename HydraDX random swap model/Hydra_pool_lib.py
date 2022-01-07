#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("running file: Hydra_pool_lib.py")
import numpy as np
class Pool :
           
    def __init__(self, base_id, asset_id:1,  R, S, C,  price, a):#Token id, Reserve of Token, Share, Coefficient, Price in Q
    #Q - Базовая ликвидность пула - это общее количество базового актива (HDX) внутри пула. 
        
        self.pool = {
                        # 'asset_id' : asset_id,
                        asset_id :{
                        'R': R,
                        'S': S,
                        'C': C,
                        'W' : S,
                       # 'P': price
                         }, 
                        base_id:{
                         'R': R*price, 
                         'S': S,
                         'C': C,
                         'W': S 
                        }, 
                        'Total_S':2*S,
                        'a':a}
#------------------
  
#-----------------------------
    def add_new_asset(self, base_id, asset_id, R, C, price):
        tot_s=self.pool['Total_S']
        tot_q = self.pool[base_id]['R']
        sum_r = R*price
        S = R*price*tot_s/tot_q/2
        print('check error = ',tot_s, tot_q, sum_r, S)
        
        self.pool.update({
                        # 'asset_id' : asset_id,
                        asset_id :{
                        'R': R,
                        'S': S,
                        'C': C,
                        'W' : S
                        #'P': price
                        },
                        
                        base_id:{
                        'R': self.pool[base_id]['R']+R*price,
                        'S':self.pool[base_id]['S']+S,
                        'C': self.pool[base_id]['C']+C,
                        'W':self.pool[base_id]['W']+ S },
                        'Total_S':self.pool['Total_S']+2*S
                        })
        
        
       
     
#-----------------------
    def BaseTokenRatio(self):
        return self.pool[0]['S']/self.pool[0]['R']
    
    def spotpriceR(self, token1, token2):
        return self.pool[token1]['R']*self.pool[token2]['S']/self.pool[token2]['R']/self.pool[token1]['S']
    
    def spotpriceQ(self, token1):
        return self.pool[0]['R']*self.pool[token1]['S']/self.pool[token1]['R']/self.pool[0]['S']
    
    def mintQ(self, token1, delta_R):
        return pool.spotpriceQ(token1)*delta_R
        
    def mintS(self, token1, delta_R):
        return pool.BaseTokenRatio()*pool.mintQ(token1, delta_R)
    
    def burnS(self, token1, delta_R):
        return pool.BaseTokenRatio()*pool.burnQ(token1, delta_R)
    
    def burnQ(self, token1, delta_R):
        return pool.spotpriceQ(token1)*delta_R
#------------------------------    
    def add_liquidity_pool(self, asset_id, delta_R):#, delta_S, delta_C):
        a = self.pool['a']
        Si = self.get_share(asset_id) 
        Ri = self.get_reserve(asset_id)
        #Ci = self.get_coefficient(asset_id)
        for key in self.pool.keys():            
            if key == asset_id:
                self.pool[key]['R'] += delta_R
                #self.pool[key]['S'] += pool.mintS(asset_id, delta_R)
                self.pool[key]['S'] = Si * (Ri - delta_R) / Ri
                #self.pool[key]['C'] = Ci * ((Ri + delta_R) / Ri) ** (a+1)
                self.pool[key]['W']  = pool[key]['S']#pool.W(asset_id)
                
                self.pool[0]['S']  += pool.mintS(asset_id, delta_R)
                self.pool[0]['R']  += pool.mintQ( asset_id, delta_R)
                self.pool['Total_S']  += pool.mintS(self, asset_id, delta_R)*2
         # Здесь работаю !!!
            
            
    def remove_liquidity_pool(self, asset_id, delta_R):#, delta_S, delta_C, a):
        a = self.pool['a']
        Si = self.get_share(asset_id) 
        #Ci = self.get_coefficient(asset_id)
        Ri = self.get_reserve(asset_id)
        for key in self.pool.keys():
            if key == asset_id:
                self.pool[key]['R'] -= delta_R
                self.pool[key]['S'] = Si * (Ri - delta_R) / Ri
                #self.pool[key]['S'] -= pool.burnS(asset_id, delta_R)
                #self.pool[key]['C'] = Ci * ((Ri - delta_R) / Ri) ** (a+1)
                self.pool[key]['W']  = pool[key]['S']#pool.W(asset_id)
                
                self.pool[0]['S']  -= pool.burnS(asset_id, delta_R)
                self.pool[0]['R']  -= pool.burnQ( asset_id, delta_R)
                self.pool['Total_S']  -= pool.burnS(asset_id, delta_R)*2
                
    def after_swap_r_r_pool_update(self, asset_in, amount_in, asset_out, amount_out):
        a = self.pool['a']
        for key in self.pool.keys():
            #print('key = ', key)
            if key == asset_in:
                #Ci = self.get_coefficient(asset_in)
                Ri = self.get_reserve(asset_in)
                Si = self.get_share(asset_in) 
                self.pool[key]['R'] += amount_in
                #self.pool[key]['S'] += pool.mintS(asset_in, amount_in)
                self.pool[key]['S'] = Si * (Ri + amount_in) / Ri
                #self.pool[key]['C'] = Ci * ((Ri + amount_in) / Ri) ** (a+1)
                self.pool[key]['W']  = self.pool[key]['S']#pool.W(asset_in)
            if key == asset_out:
                #Ci = self.get_coefficient(asset_out)
                Ri = self.get_reserve(asset_out)
                Si = self.get_share(asset_out) 
                self.pool[key]['R'] -= amount_out
                #self.pool[key]['S'] -= pool.burnS(asset_out, amount_out)
                self.pool[key]['S'] = Si * (Ri - amount_out) / Ri
                #self.pool[key]['C'] = Ci * ((Ri - amount_out) / Ri) ** (a+1)
                self.pool[key]['W']  = self.pool[key]['S']#pool.W(asset_out)
#-------------------------------------------------------  
    def after_swap_r_q_pool_update(self, asset_in, amount_in, asset_out, amount_out):
        a = self.pool['a']
        for key in self.pool.keys():
            #print('key = ', key)
            if key == asset_in:#r
                Ci = self.get_coefficient(asset_in)
                Ri = self.get_reserve(asset_in)
                Si = self.get_share(asset_in) 
                self.pool[key]['R'] += amount_in
                #self.pool[key]['S'] += pool.mintS(asset_in, amount_in)
                self.pool[key]['S'] = Si * (Ri + amount_in) / Ri
                #self.pool[key]['C'] = Ci * ((Ri + amount_in) / Ri) ** (a+1)
                self.pool[key]['W']  = self.pool[key]['S']#pool.W(asset_in)
            if key == asset_out:#Q
                Ci = self.get_coefficient(asset_out)
                Ri = self.get_reserve(asset_out)
                Si = self.get_share(asset_out) 
                self.pool[key]['R'] -= amount_out
                #self.pool[key]['S'] -= pool.burnS(asset_out, amount_out)
                self.pool[key]['S'] = Si * (Ri - amount_out) / Ri
                #self.pool[key]['C'] = Ci * ((Ri - amount_out) / Ri) ** (a+1)
                self.pool[key]['W']  = self.pool[key]['S']#pool.W(asset_out)
#--------------------------------------------------
   
    def q_to_r_pool(self, asset_id, delta_R):
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                self.pool[key]['R'] -= delta_R

    def r_to_q_pool(self, asset_id, delta_R):
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                self.pool[key]['R'] += delta_R
                
    def get_price_in_q(self, asset_id):
        for key in self.pool.keys():
            if key == asset_id:
                return(self.pool[0]['R']*self.pool[asset_id]['W']/self.pool[asset_id]['R']/self.pool[0]['W'])

            
    def get_price_i_in_j(self, asset_i, asset_j):#  Need for Chech !!!!
        for key in self.pool.keys():
            if key == asset_i:
                return(self.pool[asset_j]['R']*self.pool[asset_i]['W']/self.pool[asset_i]['R']/self.pool[asset_j]['W'])
            
    def get_reserve(self, asset_id):
        """
        returns reserve R of one specific asset from the pool variable
        """
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                return(self.pool[key]['R'])

    def get_share(self, asset_id):
        """
        returns share S of one specific asset from the pool variable
        """
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                return(self.pool[key]['S'])

    def get_weight(self, asset_id):
        """
        returns weight W of one specific asset from the pool variable
        """
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                return(self.pool[key]['W'])

    def get_coefficient(self, asset_id):
        """
        returns coefficient C of one specific asset from the pool variable
        """
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                return(self.pool[key]['C'])
            
    def get_info(self, asset_id):
        for key in self.pool.keys():
            # print(self.pool.items()) 
            if key == asset_id:
                return(self.pool[key])
            
    def get_a(self):
        return(self.pool['a'])
            
    def set_R_in(self, asset_id, amount_in):
        for key in self.pool.keys():
            if key == asset_id:
                self.pool[key]['R']=self.pool[key]['R']+amount_in
    
    def set_R_out(self, asset_id, amount_out):
        for key in self.pool.keys():
            if key == asset_id:
                self.pool[key]['R']=self.pool[key]['R']-amount_out

    def r_to_r_constant(self, asset_in, asset_out):
        return self.pool[asset_in]['C']*(self.pool[asset_in]['R']**self.pool['a'])+self.pool[asset_out]['C']*(self.pool[asset_out]['R']**self.pool['a'])
    
    def Y(self):
        summa=0
        a = self.pool['a']
        for key in self.pool.keys(): 
            if key != 0 and key!='Total_S' and key!='a':
                summa += self.pool[key]['C']*(self.pool[key]['C']**(-a))
        return (summa**(-1/a))
    
    def Z(self):
        return (self.pool[0]['R']**0.5)*(pool.Y()**0.5)
    
    def W(self, asset_in):
        a = self.pool['a']
        res=0
        for key in self.pool.keys(): 
            if key == asset_in:
                res = self.pool[key]['C']*(pool.Y()**a)/(self.pool[key]['C']**a)
        return res
            
    def Pq(self, asset_in):
        return self.pool[0]['R']*pool.W(asset_in)/self.pool[asset_in]['R']
    
    def C(self, asset_in):
        a = self.pool['a']
        return pool.W(asset_in)*(self.pool[asset_in]['R']**a)/(pool.Y()**a)
    
    def get_Q(self):
        return self.pool[0]['R']
#----------
    def __str__(self):
        """
        Print all attributes of an event
        """
        return str(self.__class__) + ": " + str(self.__dict__)   
print("End of file: Hydra_pool_lib.py")


# In[2]:


#Hydra SWAP
#https://hackmd.io/@poliwop/ryeUYgVn_#Swap-Risk-Assets
def calc_out_q_given_in_r(pool, amount_in, token_in, token_out, fee):
    a= pool.get_a()
    q= pool.get_Q()
    y = pool.Y()
    return q*y*((y**(-a) - pool.get_info(token_in)['C']*(pool.get_info(token_in)['R']**(-a))+ pool.get_info(token_in)['C']*((pool.get_info(token_in)['R']+amount_in)**(-a)) )**(1/a)) - q
#-----------------------------
def calc_out_r_given_in_q(pool, amount_in, token_in, token_out, fee):
    a= pool.get_a()
    q= pool.get_Q()
    y = pool.Y()
    return (((q*y/(q+amount_in))**(-a))/pool.get_info(token_in)['C']    -(y**(-a))/pool.get_info(token_in)['C']+(pool.get_info(token_in)['R']**(-a)))**(-1/a) - pool.get_info(token_out)['R']
#-------------------------
def calc_out_given_in_balancer(pool,amount_in, token_in, token_out, fee):
    out = pool.get_info(token_out)['R']*(1-(pool.get_info(token_in)['R']/(pool.get_info(token_in)['R']+amount_in*(1-fee)))**(pool.get_info(token_in)['W']/pool.get_info(token_out)['W']))
    return out
#------------------------------
def calc_out_given_in_hydra1(pool,amount_in, token_in, token_out, fee):
    a= pool.get_a()
    out = 10
    if token_in =='0' :
        out= calc_out_r_given_in_q(pool, amount_in, token_in, token_out, fee)
    elif token_out =='0' :
        out = calc_out_q_given_in_r(pool, amount_in, token_in, token_out, fee)
    else:
        #print('Token in, out = ', token_in, token_out)
        sk1=pool.get_info(token_in)['C']*(pool.get_info(token_in)['R']**(-a))/pool.get_info(token_out)['C']
        sk2=pool.get_info(token_in)['C']*((pool.get_info(token_in)['R']+amount_in*(1-fee))**(-a))/pool.get_info(token_out)['C']
        sk3=pool.get_info(token_out)['R']**(-a)
        out = - (sk1- sk2+ sk3)**(-1/a) + pool.get_info(token_out)['R']
    return out
#------------------------
def swap_hydra2 (pool,amount_in, token_in, token_out, fee):
    re = 'SWAP ERROR'
    amount_out = calc_out_given_in_hydra1(pool,amount_in, token_in, token_out, fee)
    if token_in =='0':
        if amount_out>0 and pool.get_reserve(token_out)>amount_out and pool.get_share(token_in)>0 and pool.get_share(token_out)>0:
            after_swap_r_q_pool_update(token_in, amount_in, token_out, amount_out)
            re = 'SWAP OK !'
    elif token_out =='0':
        if amount_out>0 and pool.get_reserve(token_out)>amount_out and pool.get_share(token_in)>0 and pool.get_share(token_out)>0:
            after_swap_r_q_pool_update(token_in, amount_in, token_out, amount_out)
            re = 'SWAP OK !'
    else:
        if amount_out>0 and pool.get_reserve(token_out)>amount_out and pool.get_share(token_in)>0 and pool.get_share(token_out)>0:
            pool.after_swap_r_r_pool_update(token_in, amount_in, token_out, amount_out)
            re = 'SWAP OK !'
    return [amount_out, re]


# In[ ]:




