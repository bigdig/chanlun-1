# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 14:01:12 2017

@author: gyrx-zstzgy07
"""

import pickle
from chan import Chan
import numpy as np
import time as ti
import datetime as dt
from pandas import DataFrame
from WindPy import *
import threading

def nowTime():
    nowT = ti.strftime('%Y-%m-%d %H:%M:%S',ti.localtime(ti.time()))
    return nowT

def feedData():
    w.start()
    code = '300002.SZ'
#    with open(r'C:\Users\gyrx-zstzgy07\Desktop\chan\创业板30分K\%s.pkl' % code, 'rb') as f:
#        data = pickle.load(f)
#    nowTime = ti.strftime('%Y-%m-%d %H:%M:%S',ti.localtime(ti.time()))
    
    #dataToNowDf = DataFrame(index=dataToNow.Times,data = dataToNow.Data[0],columns=['price'])
    #dataToNowDf = dataToNowDf.between_time('9:30','11:30').append(dataToNowDf.between_time('13:00','15:00'))

    #a = dataToNowDf.resample('30T',how = {'price':'ohlc'},label='right').dropna()
    
    def myCallback(indata):
        if indata.ErrorCode!=0:
            print('error code:'+str(indata.ErrorCode)+'\n');
            return
        dateStr = str(indata.Data[0][0])[:-2]+str(indata.Data[1][0])[:-2]
        t = dt.datetime.strptime(dateStr,'%Y%m%d%H%M%S')
        if t == dataToNow.Times[-1]:
            return
        dataToNow.Times.append(t)
        dataToNow.Data[0].append(indata.Data[2][0])
        print(t)
        print(indata.Data[2][0])
    aa = 0
    while aa<1000:
        myCallback(w.wsq(code,"rt_date,rt_time,rt_last"))
        aa += 1
        ti.sleep(1)
    
    
#datetime.datetime.strptime('20170207150003','%Y%m%d%H%M%S')
#
#str(b.Data[0][0])[:-2]+str(b.Data[1][0])[:-2]


