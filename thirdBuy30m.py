# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 14:27:13 2017

@author: gyrx-gy022
"""

from chan import *
from WindPy import *
import pickle
from pandas import DataFrame
import datetime
import bisect
#==============================================================================
#
#==============================================================================

w.start()
codeList = w.wset("sectorconstituent",
                  "date=2017-01-13;sectorid=a001010r00000000")

#codeList = w.wset("sectorconstituent","date=2017-02-01;windcode=000905.SH")

result = DataFrame(index=codeList.Data[1], columns=[
                   'date', 'price', 'ret'])

j=0
for code in codeList.Data[1][0:400]:
    j+=1
    print(code)
#    data = pickle.load(
#        open(r'C:\Users\lizard\Desktop\chan\创业板30分K\%s.pkl' % code, 'rb'))
    with open(r'C:\Users\lizard\Desktop\chan\创业板30分K\%s.pkl' % code, 'rb') as f:
        data = pickle.load(f)
    #print(code)
    # data = w.wsd(code, "open,high,low,close,volume", "2014-01-01", "2017-01-01", "PriceAdj=F")

    start = 0
    end = len(data.Data[0])-300
    chan = Chan(data.Data[0][start:end], data.Data[1][start:end], data.Data[2][
                start:end], data.Data[3][start:end], data.Data[4][start:end], data.Times[start:end])

    thirdBuy = []
    thirdSell = []
    isInThirdBuy = 0
    Lastzhongshu = 0
    try:
        for tick in range(end+1, len(data.Times)):
            chan.append(data.Data[0][tick], data.Data[1][tick], data.Data[2][
                        tick], data.Data[3][tick], data.Data[4][tick], data.Times[tick])
            chan.barsMerge()
            chan.findFenxing()
            chan.findBi()
            chan.findLines()
            chan.findZhongshus()
            #chan.calculate_ta()
            #chan.findBiZhongshus()
            #chan.macdSeparate()

            # Make sure there's at least one zhongshu
            try:
                zhongshu = chan.zhongshus[-1]
            except:
                continue

            if isInThirdBuy == 1:
                if chan.lines[-1].lineType == 'up':
                    continue
                else:
                    thirdSell.append(data.Times[tick])
                    isInThirdBuy = 0

            if len(chan.lines) >= 2:
                if chan.lines[-1].lineType == 'up' and chan.lines[-2].lineType == 'down':

                    if chan.chanBars[chan.lines[-2].barIndex1].high > zhongshu.high and chan.chanBars[chan.lines[-2].barIndex2].low > zhongshu.high:
                        if (chan.chanBars[chan.lines[-2].barIndex1].closeTime - chan.chanBars[zhongshu.barIndex2].closeTime)/datetime.timedelta(1) < 60: #check line and zhongshu are not too far
                            if data.Data[3][tick] > zhongshu.high and Lastzhongshu != zhongshu.barIndex1:
                                # Start third buy
                                #print('oops')
                                isInThirdBuy = 1
                                thirdBuy.append(data.Times[tick])
                            else:
                                Lastzhongshu = zhongshu.barIndex1
#                            print('oops')
#                            isInThirdBuy = 1
#                            thirdBuy.append(data.Times[tick])

        if len(thirdBuy) != len(thirdSell):
            thirdSell.append(data.Times[tick])
            
        
        startPrice = []
        endPrice = []
        ret = []
        for i in range(len(thirdBuy)):
            startPrice.append(chan.closeBar[chan.closeTime.index(thirdBuy[i])])
            endPrice.append(chan.closeBar[chan.closeTime.index(thirdSell[i])])
            ret.append((endPrice[-1]-startPrice[-1])/startPrice[-1])
        result.loc[code, 'date'] = list(zip(thirdBuy,thirdSell))
        result.loc[code, 'price'] = list(zip(startPrice,endPrice))
        result.loc[code, 'ret'] = ret
    except:
        continue
    
#result.to_pickle(r'C:\Users\lizard\Desktop\chan\result_notfar2_higher.pkl')
