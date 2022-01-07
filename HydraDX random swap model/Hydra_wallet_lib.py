#!/usr/bin/env python
# coding: utf-8

# In[ ]:


print("Running file: Hydra_wallet_lib.py")
class Wallet:
    def __init__(self,  tokenList):
        self.list = tokenList
        
        
    def addTokenToWallet(self,tl):
        self.list.update(tl)
        
    def sendTokenAmountFromWallet(self, token, amount_out):
        #print('Full list = ',self.list.items()) 
        count=0
        for key in self.list.keys():
            if key == token:
                count=count+1
                if amount_out<=self.list[key]:
                    self.list[key]=self.list[key]-amount_out
                    print('Send is made, Rest ot ', token, ' is ',self.list[key] )
                    count=count+1
                else:
                    print('No asked amount = ', amount_out, ', there is ', self.list[key])
                    return False
        if count==0:
            print('No this token= ', token , 'on Wallet !!')
        if count==2:
            return True
        else:
            return False
    
    def receiveTokenAmountToWallet(self, token, amount_in ):
        count=0
        for key in self.list.keys():
            if key == token:
                count=count+1
                self.list[key]= self.list[key]+amount_in
                print('Amount Added')
        if count==0:
                self.list.update({token: amount_in})
                print('Token and amount Added')
    
    def get_info(self):
        return self.list

print("End of file: Hydra_wallet_lib.py")

