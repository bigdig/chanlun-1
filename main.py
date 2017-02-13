# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:05:33 2016

@author: gyrx-gy022
"""

from chan import *
from WindPy import *
#==============================================================================
# 
#==============================================================================
w.start()
data = w.wsd("000300.SH", "open,high,low,close,volume", "2015-01-1", "2015-12-31", "")
#data = w.wsi("000001.SH", "open,high,low,close,volume", "2016-01-01 09:00:00", "2016-11-24 15:30:00", "BarSize=5")

#%%        
start = 0
end = len(data.Data[0])
chan = Chan(data.Data[0][start:end],data.Data[1][start:end],data.Data[2][start:end],data.Data[3][start:end],data.Data[4][start:end],data.Times[start:end])
chan.barsMerge()
chan.findFenxing()
chan.findBi()
chan.findLines()
chan.findZhongshus()
chan.calculate_ta()
chan.plot()