# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 19:58:09 2017

@author: lizard
"""

from chan import *
from WindPy import *
import pickle
import bisect
from pandas import DataFrame
import numpy as np
#==============================================================================
# 
#==============================================================================
result = pickle.load(open(r'C:\Users\lizard\Desktop\chan\result_notfar2_higher.pkl', 'rb'))
chuangyeban = pickle.load(open(r'C:\Users\lizard\Desktop\chan\创业板5分K\399006.SZ.pkl','rb'))

equity = DataFrame(index=chuangyeban.Times,columns = ['ret'])

for i in equity.index:
    equity.loc[i,'ret'] = []
    
for code,j in result.iloc[:200].iterrows():
    with open(r'C:\Users\lizard\Desktop\chan\创业板5分K\%s.pkl' % code, 'rb') as f:
        data = pickle.load(f)
    print(code)
    if type(j['date']) != list:
        continue
    for num in range(len(j['date'])):
        start = chuangyeban.Times.index(j['date'][num][0])
        end = chuangyeban.Times.index(j['date'][num][1])
        for i in range(start,end):
            ret = (data.Data[3][i+1]-data.Data[3][i])/data.Data[3][i]# - (chuangyeban.Data[3][i+1]-chuangyeban.Data[3][i])/chuangyeban.Data[3][i]
            equity.iloc[i+1,0].append(ret)
            
equity['equityRet'] = equity.ret.apply(np.mean)
equity = equity.fillna(value=0)

#a = np.cumprod(np.array(equity.equityRet.values)+1)
a = np.cumsum(np.array(equity.equityRet.values))+1