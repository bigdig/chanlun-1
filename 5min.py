# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:07:56 2017

@author: lizard
"""
from chan import *
from WindPy import *
import pickle
import bisect
from pandas import DataFrame
#==============================================================================
# 
#==============================================================================
result = pickle.load(open(r'C:\Users\lizard\Desktop\chan\result_notfar2.pkl', 'rb'))
result5min = DataFrame(index=result.index, columns=[
                   'date', 'price', 'ret','retExceed'])

chuangyeban = pickle.load(open(r'C:\Users\lizard\Desktop\chan\创业板5分K\399006.SZ.pkl','rb'))

def findPeaks(series):
    peaks = []
    for i in range(1,len(series)-1):
        if series[i] > series[i-1] and series[i] > series[i+1]:
            peaks.append(series[i])
    return peaks




for code,j in result.iloc[:200].iterrows():
    data = pickle.load(
            open(r'C:\Users\lizard\Desktop\chan\创业板5分K\%s.pkl' % code, 'rb'))
    print(code)
    if type(j['date']) != list:
        continue
    date = []
    price = []
    ret = []
    retExceed = []
    for num in range(len(j['date'])):
        startTime = j['date'][num][0]
        endTime = j['date'][num][1]
        start = bisect.bisect(data.Times,startTime)
        end = bisect.bisect(data.Times,endTime)
        chan5m = Chan(data.Data[0][start-200:start],data.Data[1][start-200:start],data.Data[2][start-200:start],data.Data[3][start-200:start],data.Data[4][start-200:start],data.Times[start-200:start])
        numOfBis = 10
        searchBis = []
        
        foundSell = 0
        for tick in range(start, end):
            try:
                chan5m.append(data.Data[0][tick], data.Data[1][tick], data.Data[2][
                            tick], data.Data[3][tick], data.Data[4][tick], data.Times[tick])
                chan5m.barsMerge()
                chan5m.findFenxing()
                chan5m.findBi()
                chan5m.calculate_ta()
                chan5m.macdSeparate()
                chan5m.findBiZhongshus()
                if chan5m.bis[-1].biType == 'up':
                    continue
                if chan5m.bis[-1].barIndex2 - chan5m.bis[-1].barIndex1 < 4:
                    continue
                searchBis = chan5m.bis[-numOfBis:]
            
            
                searchPeaks = []
                for b in searchBis:
                    if b.biType == 'up':
                        searchPeaks.append(chan5m.highBar[chan5m.chanBars[b.barIndex2].closeIndex])
                           
                if searchPeaks[-1] >= max(searchPeaks[:-2]) and searchPeaks[-1] >= searchPeaks[-2]*0.97: #and searchPeaks[-1]>chan5m.biZhongshus[-1].high*1.05:
                    #check macd
                    searchStart = chan5m.chanBars[searchBis[0].barIndex1].closeIndex
                    searchEnd = chan5m.chanBars[searchBis[-1].barIndex2].closeIndex
                    macdPeaks = findPeaks(chan5m.macd[searchStart:searchEnd])
            
            #        bi1 = chan5m.bis.index(searchBis[-1])
            #        bi2 = chan5m.bis.index(searchBis[-3])
            #        bi3 = chan5m.bis.index(searchBis[-5])
                    #if chan5m.matchMacd2(bi1) <= chan5m.matchMacd2(bi2) and chan5m.matchMacd2(bi1) <= chan5m.matchMacd2(bi3):
                    if macdPeaks[-1] <= max(macdPeaks[:-1]):
                        #背驰
                        ret.append((data.Data[3][tick] - j['price'][num][0])/j['price'][num][0])
                        
                        date.append((j['date'][num][0],data.Times[tick]))
                        price.append((j['price'][num][0],data.Data[3][tick]))
                        retChuangyeban = (chuangyeban.Data[3][tick] - chuangyeban.Data[3][start])/chuangyeban.Data[3][start]
                        retExceed.append((data.Data[3][tick] - j['price'][num][0])/j['price'][num][0] - retChuangyeban)
                        foundSell = 1
                        break
            except:
                break
        if foundSell == 0:
            date.append(j['date'][num])
            price.append(j['price'][num])
            ret.append(j['ret'][num])
            retChuangyeban = (chuangyeban.Data[3][tick] - chuangyeban.Data[3][start])/chuangyeban.Data[3][start]
            retExceed.append((data.Data[3][tick] - j['price'][num][0])/j['price'][num][0] - retChuangyeban)
            
    result5min.loc[code, 'date'] = date
    result5min.loc[code, 'price'] = price
    result5min.loc[code, 'ret'] = ret
    result5min.loc[code, 'retExceed'] = retExceed