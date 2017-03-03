# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:05:33 2016

@author: gyrx-gy022
"""

import sys
sys.path.append('./')
sys.path.append('../')
import pandas as pd

from chan import *

class ValuesParser:
    def __init__(self,dataframe):
        self.Data = [data['open'].tolist(),data['high'].tolist(),data['low'].tolist(),data['close'].tolist(),data['volume'].tolist()]
        self.Times= data.index
        print(self.Times)


data = pd.DataFrame.from_csv('rb1705.csv')

data = ValuesParser(data)
start = 0
end = len(data.Times)
chan = Chan(data.Data[0][start:end],data.Data[1][start:end],data.Data[2][start:end],data.Data[3][start:end],data.Data[4][start:end],data.Times[start:end])
#chan = Chan(data['open'],data['high'],data['low'],data['close'],data['volume'],data['open'])
chan.barsMerge()
chan.findFenxing()
chan.findBi()
chan.findLines()
chan.findZhongshus()
chan.calculate_ta()
chan.plot()
