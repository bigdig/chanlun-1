# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 14:27:13 2017

@author: gyrx-gy022
"""

from chan import *
from WindPy import *
import pickle
from pandas import DataFrame
import tushare as ts
#==============================================================================
# 
#==============================================================================

w.start()
codeList = w.wset("sectorconstituent","date=2017-01-13;sectorid=a001010r00000000")
result = DataFrame(index=codeList.Data[1][0:400],columns=['startDate','endDate','startPrice','endPrice','ret','openPosition'])

for code in codeList.Data[1][0:400]:
    data = pickle.load(open(r'C:\Users\gyrx-gy022\Desktop\chan\创业板日K\%s.pkl' %code,'rb'))

    #data = w.wsd(code, "open,high,low,close,volume", "2014-01-01", "2017-01-01", "PriceAdj=F")

    openPosition = 0
    start = 0
    end = 300
    chan = Chan(data.Data[0][start:end],data.Data[1][start:end],data.Data[2][start:end],data.Data[3][start:end],data.Data[4][start:end],data.Times[start:end])

    
    thirdBuy = []
    try:
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
            if len(chan.lines)>=2:
                if chan.lines[-1].lineType == 'up' and chan.lines[-2].lineType == 'down':
                    
                    if chan.chanBars[chan.lines[-2].barIndex1].high > zhongshu.high and chan.chanBars[chan.lines[-2].barIndex2].low > zhongshu.high*0.9:
                        if openPosition == 0:
                            openPosition = chan.chanBars[chan.lines[-2].barIndex2].low/zhongshu.high
                        thirdBuy.append(data.Times[tick])
            
                        if data.Data[3][tick] < zhongshu.high:
                            break
        result.loc[code,'startDate'] = thirdBuy[0]
        result.loc[code,'endDate'] = thirdBuy[-1]
        result.loc[code,'startPrice'] = chan.closeBar[chan.closeTime.index(thirdBuy[0])]
        result.loc[code,'endPrice'] = chan.closeBar[chan.closeTime.index(thirdBuy[-1])]
        result.loc[code,'ret'] = (result.loc[code,'endPrice']-result.loc[code,'startPrice'])/result.loc[code,'startPrice']
        result.loc[code,'openPosition'] = openPosition
    except:
        continue