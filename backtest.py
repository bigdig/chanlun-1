# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 16:33:32 2016

@author: gyrx-gy022
"""

from chan import *
from WindPy import *
import pickle
#==============================================================================
# 
#==============================================================================
result = pickle.load(open(r'C:\Users\lizard\Desktop\chan\result_notfar.pkl', 'rb'))

w.start()
data = w.wsd("300009.SZ", "open,high,low,close,volume", "2014-01-01", "2017-01-01", "")
#data = w.wsi("300009.SZ", "open,high,low,close,volume", "2012-08-01 09:00:00", "2016-12-01 15:30:00", "BarSize=30","PriceAdj=F")
#data = pickle.load(open(r'/Users/linmuchen/Documents/工作/缠论/dataDay.pkl','rb'))
#==============================================================================
# 
#==============================================================================
start = 0
end = len(data.Times)
#chan = Chan(data['data'][0][start:end],data['data'][1][start:end],data['data'][2][start:end],data['data'][3][start:end],data['data'][4][start:end],data['time'][start:end])
chan = Chan(data.Data[0][start:end],data.Data[1][start:end],data.Data[2][start:end],data.Data[3][start:end],data.Data[4][start:end],data.Times[start:end])
#chan.barsMerge()
#chan.findFenxing()
#chan.findBi()
#chan.findLines()
#chan.findZhongshus()
#chan.calculate_ta()

thirdBuy = []
for tick in range(301,len(data.Times)):
    chan.append(data.Data[0][tick],data.Data[1][tick],data.Data[2][tick],data.Data[3][tick],data.Data[4][tick],data.Times[tick])
    chan.barsMerge()
    chan.findFenxing()
    chan.findBi()
    chan.findLines()
    chan.findZhongshus()
    chan.calculate_ta()
    chan.findBiZhongshus()
    chan.macdSeparate()
    try:
        zhongshu = chan.zhongshus[-1]
    except:
        continue
    if chan.lines[-1].lineType == 'up' and chan.lines[-2].lineType == 'down':
        
        if chan.chanBars[chan.lines[-2].barIndex1].high > zhongshu.high and chan.chanBars[chan.lines[-2].barIndex2].low > zhongshu.high*0.9:
            thirdBuy.append(data.Times[tick])
    





#for tick in range(401,1670):
#    chan.append(data['data'][0][tick],data['data'][1][tick],data['data'][2][tick],data['data'][3][tick],data['data'][4][tick],data['time'][tick])
#    chan.barsMerge()
#    chan.findFenxing()
#    chan.findBi()
#    chan.findLines()
#    chan.findZhongshus()
#    chan.findBiZhongshus()
#    chan.calculate_ta()
#    chan.macdSeparate()
#    chan.decisionBi()
#chan.plotBeichi()
#    