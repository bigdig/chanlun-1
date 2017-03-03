# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 09:06:39 2016

@author: gyrx-gy022
"""
#==============================================================================
# 
#==============================================================================
import pandas as pd
import os 
import numpy as np
import datetime
import bisect
from dateutil.parser import parse
import statsmodels.api as sm
import warnings
from ta import *

np.set_printoptions(threshold=np.inf)
warnings.simplefilter(action = 'ignore',category = RuntimeWarning)
#==============================================================================
# 
#==============================================================================
#get_ipython().magic('matplotlib inline')

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.finance import candlestick_ohlc
matplotlib.style.use('ggplot')


#==============================================================================
# 
#==============================================================================
#%%
class ChanBar(object):
    def __init__(self,open,high,low,close,volume,startTime,closeTime,closeIndex):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.startTime = startTime
        self.closeTime = closeTime
        self.closeIndex = closeIndex  #在原始的Bar上的实际Index
        self.isMerged = False  #是否由几根bar合成
        self.numOfBars = 1   #包含的bar数目
    def describe(self):
        print('open:',self.open)
        print('high:',self.high)
        print('low:',self.low)
        print('close:',self.close)
        print('volume:',self.volume)
        print('startTime:',self.startTime)
        print('closeTime:',self.closeTime)
        print('isMerged:',self.isMerged)
        print('numOfBars:',self.numOfBars)
        
class fenxing(object):
    def __init__(self,barIndex1,barIndex2,barIndex3,fenxingType):
        self.barIndex1 = barIndex1
        self.barIndex2 = barIndex2
        self.barIndex3 = barIndex3
        self.fenxingType = fenxingType
    def describe(self):
        print('bars at:',self.barIndex1,self.barIndex2,self.barIndex3)
        print('FenXingType:',self.fenxingType)
        
class bi(object):
    def __init__(self,barIndex1,barIndex2,biType):
        self.barIndex1 = barIndex1
        self.barIndex2 = barIndex2
        self.biType = biType
        
class line(object):
    def __init__(self,barIndex1,barIndex2,lineType,featureHigh,featureLow,featureHighIndex,featureLowIndex,featureBiIndex):
        self.barIndex1 = barIndex1
        self.barIndex2 = barIndex2
        self.lineType = lineType
        self.featureHigh = featureHigh
        self.featureLow = featureLow
        self.featureHighIndex = featureHighIndex
        self.featureLowIndex = featureLowIndex
        self.featureBiIndex = featureBiIndex
        
class zhongshu(object):
    def __init__(self,barIndex1,barIndex2,high,low,linesIncluded):
        self.barIndex1 = barIndex1
        self.barIndex2 = barIndex2
        self.high = high
        self.low = low
        self.linesIncluded = linesIncluded
        
class Chan(object):
    def __init__(self,openBar,highBar,lowBar,closeBar,volumeBar,closeTime):
        self.openBar = openBar
        self.highBar = highBar
        self.lowBar = lowBar
        self.closeBar = closeBar
        self.volumeBar = volumeBar
        self.closeTime = closeTime
        self.length = len(self.openBar)
        #记录顶背驰
        self.dingbeichi = []
        self.trendDingbeichi = []
        self.dingbeichiLine = []
        #记录底背驰
        self.dibeichi = []
        self.trendDibeichi = []
        self.dibeichiLine = []
        #记录买卖点
        self.buy1 = []
        self.buy2 = []
        self.buy3 = []
        self.sell1 = []
        self.sell2 = []
        self.sell3 = []
        #简单回测
        self.position = 0
        self.openLong = []
        self.closeLong = []
        self.openShort = []
        self.closeShort = []
        
        self.macdBenchmarkStart = []
        self.macdBenchmarkEnd = []
        self.macdBenchmarkLastStart = []
        self.macdBenchmarkLastEnd = []
        
        self.trendLineRecord = []

    def calculate_ta(self):
        
        nslow = 26
        nfast = 12
        nema = 9
        emaslow, emafast, diff = moving_average_convergence(self.closeBar, nslow=nslow, nfast=nfast)
        dea = moving_average(diff, nema, type='exponential')
        self.diff = diff
        self.dea = dea
        self.macd = self.diff - self.dea
        
    def plot(self):
        quotes = []
        for i in range(self.length):
            quotes.append([i,self.openBar[i],self.highBar[i],self.lowBar[i],self.closeBar[i]])
            
        fig = plt.figure(figsize = (90,20))
        left, width = 0.1, 0.8
        rect1 = [left, 0.3, width, 0.6]
        rect2 = [left, 0.1, width, 0.2]
        #ax1 = fig.add_subplot(1,1,1)
        ax1 = fig.add_axes(rect1)
        ax1.set_xlim(left=0)
        ax3 = fig.add_axes(rect2, sharex=ax1)
        matplotlib.finance.candlestick_ohlc(ax1,quotes,width=1,colordown='g',colorup='r')
        fillcolor = 'darkslategrey'
        ax3.plot(range(self.length), self.diff, color='white', lw=2)
        ax3.plot(range(self.length), self.dea, color='yellow', lw=1)
        ax3.fill_between(range(self.length), self.macd, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor) 
#        for fenxing in self.fenxings:
#            if fenxing.fenxingType == 'ding':
#                ax1.add_patch(
#                    patches.Rectangle(
#                        (fenxing.barIndex1, min(self.chanBars[fenxing.barIndex1].low,self.chanBars[fenxing.barIndex3].low)),
#                        2,
#                        self.chanBars[fenxing.barIndex2].high - min(self.chanBars[fenxing.barIndex1].low,self.chanBars[fenxing.barIndex3].low),
#                        fill=False,      # remove background
#                        ec = 'r'
#                    )
#                )
#            else:
#                ax1.add_patch(
#                    patches.Rectangle(
#                        (fenxing.barIndex1, self.chanBars[fenxing.barIndex2].low),
#                        2,
#                        max(self.chanBars[fenxing.barIndex1].high,self.chanBars[fenxing.barIndex3].high) - self.chanBars[fenxing.barIndex2].low,
#                        fill=False,      # remove background
#                        ec = 'b'
#                    )
#                )
        
        for bi in self.bis:
            if bi.biType == 'up':
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.lowBar[self.chanBars[bi.barIndex1].closeIndex],self.highBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'r')
            else:
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.highBar[self.chanBars[bi.barIndex1].closeIndex],self.lowBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'b')
                
        for line in self.lines:
            if line.lineType == 'up':
                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.lowBar[self.chanBars[line.barIndex1].closeIndex],self.highBar[self.chanBars[line.barIndex2].closeIndex]),color = 'y')
            else:
                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.highBar[self.chanBars[line.barIndex1].closeIndex],self.lowBar[self.chanBars[line.barIndex2].closeIndex]),color = 'g')
        
        for zhongshu in self.zhongshus:
            ax1.add_patch(
                patches.Rectangle(
                    (self.chanBars[zhongshu.barIndex1].closeIndex, zhongshu.low),
                    self.chanBars[zhongshu.barIndex2].closeIndex - self.chanBars[zhongshu.barIndex1].closeIndex,
                    zhongshu.high - zhongshu.low,
                    fill=False,      # remove background
                    ec = 'black'
                )
            )
    
    def plotBiZhongshu(self):
        quotes = []
        for i in range(self.length):
            quotes.append([i,self.openBar[i],self.highBar[i],self.lowBar[i],self.closeBar[i]])
            
        fig = plt.figure(figsize = (90,20))
        left, width = 0.1, 0.8
        rect1 = [left, 0.3, width, 0.6]
        rect2 = [left, 0.1, width, 0.2]
        #ax1 = fig.add_subplot(1,1,1)
        ax1 = fig.add_axes(rect1)
        ax1.set_xlim(left=0)
        ax3 = fig.add_axes(rect2, sharex=ax1)
        matplotlib.finance.candlestick_ohlc(ax1,quotes,width=1,colordown='g',colorup='r')
        fillcolor = 'darkslategrey'
        ax3.plot(range(self.length), self.diff, color='white', lw=2)
        ax3.plot(range(self.length), self.dea, color='yellow', lw=1)
        ax3.fill_between(range(self.length), self.diff - self.dea, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor) 
#        for fenxing in self.fenxings:
#            if fenxing.fenxingType == 'ding':
#                ax1.add_patch(
#                    patches.Rectangle(
#                        (fenxing.barIndex1, min(self.chanBars[fenxing.barIndex1].low,self.chanBars[fenxing.barIndex3].low)),
#                        2,
#                        self.chanBars[fenxing.barIndex2].high - min(self.chanBars[fenxing.barIndex1].low,self.chanBars[fenxing.barIndex3].low),
#                        fill=False,      # remove background
#                        ec = 'r'
#                    )
#                )
#            else:
#                ax1.add_patch(
#                    patches.Rectangle(
#                        (fenxing.barIndex1, self.chanBars[fenxing.barIndex2].low),
#                        2,
#                        max(self.chanBars[fenxing.barIndex1].high,self.chanBars[fenxing.barIndex3].high) - self.chanBars[fenxing.barIndex2].low,
#                        fill=False,      # remove background
#                        ec = 'b'
#                    )
#                )
        
        for bi in self.bis:
            if bi.biType == 'up':
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.lowBar[self.chanBars[bi.barIndex1].closeIndex],self.highBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'r')
            else:
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.highBar[self.chanBars[bi.barIndex1].closeIndex],self.lowBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'b')
                
#        for line in self.lines:
#            if line.lineType == 'up':
#                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.lowBar[self.chanBars[line.barIndex1].closeIndex],self.highBar[self.chanBars[line.barIndex2].closeIndex]),color = 'y')
#            else:
#                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.highBar[self.chanBars[line.barIndex1].closeIndex],self.lowBar[self.chanBars[line.barIndex2].closeIndex]),color = 'g')
#        
        for biZhongshu in self.biZhongshus:
            ax1.add_patch(
                patches.Rectangle(
                    (self.chanBars[biZhongshu.barIndex1].closeIndex, biZhongshu.low),
                    self.chanBars[biZhongshu.barIndex2].closeIndex - self.chanBars[biZhongshu.barIndex1].closeIndex,
                    biZhongshu.high - biZhongshu.low,
                    fill=False,      # remove background
                    ec = 'black'
                )
            )
        
        trendData = zip(self.trendLineRecord,self.trendLineMacd)
        for line,label in trendData:
            ax1.annotate(round(label,2),xy=(self.chanBars[self.bis[line].barIndex1].closeIndex,self.closeBar[self.chanBars[self.bis[line].barIndex1].closeIndex]),
                                   xytext=(self.chanBars[self.bis[line].barIndex1].closeIndex+5,self.closeBar[self.chanBars[self.bis[line].barIndex1].closeIndex]+200),
                                           arrowprops=dict(facecolor='black'))
        
    
    
    def plotBeichi(self):
        dibeichi = self.dibeichi
        dingbeichi = self.dingbeichi
        delIndex = []
        for i in range(1,len(dingbeichi)):
            if dingbeichi[i] - dingbeichi[i-1] == 1:
                delIndex.append(i)
        dingbeichi = [i for j, i in enumerate(dingbeichi) if j not in delIndex]
        
        delIndex = []
        for i in range(1,len(dibeichi)):
            if dibeichi[i] - dibeichi[i-1] == 1:
                delIndex.append(i)
        dibeichi = [i for j, i in enumerate(dibeichi) if j not in delIndex]

        trendDibeichi = self.trendDibeichi
        trendDingbeichi = self.trendDingbeichi
        delIndex = []
        for i in range(1,len(trendDingbeichi)):
            if trendDingbeichi[i] - trendDingbeichi[i-1] == 1:
                delIndex.append(i)
        trendDingbeichi = [i for j, i in enumerate(trendDingbeichi) if j not in delIndex]
        
        delIndex = []
        for i in range(1,len(trendDibeichi)):
            if trendDibeichi[i] - trendDibeichi[i-1] == 1:
                delIndex.append(i)
        trendDibeichi = [i for j, i in enumerate(trendDibeichi) if j not in delIndex]
        
        fig = plt.figure(figsize = (90,20))
        left, width = 0.1, 0.8
        rect1 = [left, 0.3, width, 0.6]
        rect2 = [left, 0.1, width, 0.2]
        #ax1 = fig.add_subplot(1,1,1)
        ax1 = fig.add_axes(rect1)
        ax1.set_xlim(left=0)
        ax3 = fig.add_axes(rect2, sharex=ax1)
        #matplotlib.finance.candlestick_ohlc(ax1,quotes,width=1,colordown='g',colorup='r')
        fillcolor = 'darkslategrey'
        ax3.plot(range(self.length), self.diff, color='white', lw=2)
        ax3.plot(range(self.length), self.dea, color='yellow', lw=1)
        ax3.fill_between(range(self.length), self.diff - self.dea, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)     
        self.macdBenchmarkStart = np.sort(list(set(self.macdBenchmarkStart)))
        self.macdBenchmarkEnd = np.sort(list(set(self.macdBenchmarkEnd)))
        self.macdBenchmarkLastStart = np.sort(list(set(self.macdBenchmarkLastStart)))
        self.macdBenchmarkLastEnd = np.sort(list(set(self.macdBenchmarkLastEnd)))
        for i in range(len(self.macdBenchmarkStart)):
            ax3.axvline(x = self.macdBenchmarkStart[i],color = 'red')
            ax3.axvline(x = self.macdBenchmarkEnd[i],color = 'red')
            ax3.axvline(x = self.macdBenchmarkLastStart[i],color = 'green')
            ax3.axvline(x = self.macdBenchmarkLastEnd[i],color = 'green')
                
        for i in dibeichi:
            ax1.plot(i,self.closeBar[i],marker='*',color='black',markersize = 8)
                   
        for i in dingbeichi:
            ax1.plot(i,self.closeBar[i],marker='*',color='yellow',markersize = 8) 
            
        for i in trendDibeichi:
            ax1.plot(i,self.closeBar[i],marker='o',color='green',markersize = 10)
                   
        for i in trendDingbeichi:
            ax1.plot(i,self.closeBar[i],marker='o',color='magenta',markersize = 10)
        
        for bi in self.bis:
            if bi.biType == 'up':
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.lowBar[self.chanBars[bi.barIndex1].closeIndex],self.highBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'r')
            else:
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.highBar[self.chanBars[bi.barIndex1].closeIndex],self.lowBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'b')
        for line in self.lines:
            if line.lineType == 'up':
                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.lowBar[self.chanBars[line.barIndex1].closeIndex],self.highBar[self.chanBars[line.barIndex2].closeIndex]),color = 'y')
            else:
                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.highBar[self.chanBars[line.barIndex1].closeIndex],self.lowBar[self.chanBars[line.barIndex2].closeIndex]),color = 'g')
   
        for biZhongshu in self.biZhongshus:
            ax1.add_patch(
                patches.Rectangle(
                    (self.chanBars[biZhongshu.barIndex1].closeIndex, biZhongshu.low),
                    self.chanBars[biZhongshu.barIndex2].closeIndex - self.chanBars[biZhongshu.barIndex1].closeIndex,
                    biZhongshu.high - biZhongshu.low,
                    fill=False,      # remove background
                    ec = 'black'
                )
            )   
        

    
    def plotBuySell(self):
        """
        标记笔、 买点卖点，底背驰、顶背驰
        """
        fig = plt.figure(figsize = (45,20))
        ax1 = fig.add_subplot(1,1,1)
        for bi in self.bis:
            if bi.biType == 'up':
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.lowBar[self.chanBars[bi.barIndex1].closeIndex],self.highBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'r')
            else:
                ax1.plot((self.chanBars[bi.barIndex1].closeIndex,self.chanBars[bi.barIndex2].closeIndex),(self.highBar[self.chanBars[bi.barIndex1].closeIndex],self.lowBar[self.chanBars[bi.barIndex2].closeIndex]),color = 'b')
        for line in self.lines:
            if line.lineType == 'up':
                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.lowBar[self.chanBars[line.barIndex1].closeIndex],self.highBar[self.chanBars[line.barIndex2].closeIndex]),color = 'y')
            else:
                ax1.plot((self.chanBars[line.barIndex1].closeIndex,self.chanBars[line.barIndex2].closeIndex),(self.highBar[self.chanBars[line.barIndex1].closeIndex],self.lowBar[self.chanBars[line.barIndex2].closeIndex]),color = 'g')
   
        for biZhongshu in self.biZhongshus:
            ax1.add_patch(
                patches.Rectangle(
                    (self.chanBars[biZhongshu.barIndex1].closeIndex, biZhongshu.low),
                    self.chanBars[biZhongshu.barIndex2].closeIndex - self.chanBars[biZhongshu.barIndex1].closeIndex,
                    biZhongshu.high - biZhongshu.low,
                    fill=False,      # remove background
                    ec = 'black'
                )
            )   
            
        for i in self.openLong:
            ax1.plot(i,self.closeBar[i],marker='*',color='yellow',markersize = 6)
                   
        for i in self.closeLong:
            ax1.plot(i,self.closeBar[i],marker='*',color='black',markersize = 6) 
            
        for i in self.trendDibeichi:
            ax1.plot(i,self.closeBar[i],marker='o',color='green',markersize = 10)
                   
        for i in self.trendDingbeichi:
            ax1.plot(i,self.closeBar[i],marker='x',color='magenta',markersize = 10)
    
    def plot2(self):
        quotes = []
        for i in range(len(self.chanBars)):
            bar = self.chanBars[i]
            if bar.isMerged:
                if bar.open >= bar.close:
                    quotes.append([i,bar.high,bar.high,bar.low,bar.low])
                else:
                    quotes.append([i,bar.low,bar.high,bar.low,bar.high])
            else:
                quotes.append([i,bar.open,bar.high,bar.low,bar.close])
        fig = plt.figure(figsize = (45,20))
        ax1 = fig.add_subplot(1,1,1)
        matplotlib.finance.candlestick_ohlc(ax1,quotes,width=1,colordown='g',colorup='r')
#        for fenxing in self.fenxings:
#            if fenxing.fenxingType == 'ding':
#                ax1.add_patch(
#                    patches.Rectangle(
#                        (fenxing.barIndex1, min(self.chanBars[fenxing.barIndex1].low,self.chanBars[fenxing.barIndex3].low)),
#                        2,
#                        self.chanBars[fenxing.barIndex2].high - min(self.chanBars[fenxing.barIndex1].low,self.chanBars[fenxing.barIndex3].low),
#                        fill=False,      # remove background
#                        ec = 'r'
#                    )
#                )
#            else:
#                ax1.add_patch(
#                    patches.Rectangle(
#                        (fenxing.barIndex1, self.chanBars[fenxing.barIndex2].low),
#                        2,
#                        max(self.chanBars[fenxing.barIndex1].high,self.chanBars[fenxing.barIndex3].high) - self.chanBars[fenxing.barIndex2].low,
#                        fill=False,      # remove background
#                        ec = 'b'
#                    )
#                )
        
        for bi in self.bis:
            if bi.biType == 'up':
                ax1.plot((bi.barIndex1,bi.barIndex2),(self.chanBars[bi.barIndex1].low,self.chanBars[bi.barIndex2].high),color = 'r')
            else:
                ax1.plot((bi.barIndex1,bi.barIndex2),(self.chanBars[bi.barIndex1].high,self.chanBars[bi.barIndex2].low),color = 'b')
                
        for line in self.lines:
            if line.lineType == 'up':
                ax1.plot((line.barIndex1,line.barIndex2),(self.chanBars[line.barIndex1].low,self.chanBars[line.barIndex2].high),color = 'y')
            else:
                ax1.plot((line.barIndex1,line.barIndex2),(self.chanBars[line.barIndex1].high,self.chanBars[line.barIndex2].low),color = 'g')
        
        for zhongshu in self.zhongshus:
            ax1.add_patch(
                patches.Rectangle(
                    (zhongshu.barIndex1, zhongshu.low),
                    zhongshu.barIndex2 - zhongshu.barIndex1,
                    zhongshu.high - zhongshu.low,
                    fill=False,      # remove background
                    ec = 'black'
                )
            )
                
    def barsMerge(self):
        chanBars = []
        chanBars.append(ChanBar(self.openBar[0],self.highBar[0],self.lowBar[0],self.closeBar[0],self.volumeBar[0],self.closeTime[0],self.closeTime[0],0))
        chanBars.append(ChanBar(self.openBar[1],self.highBar[1],self.lowBar[1],self.closeBar[1],self.volumeBar[1],self.closeTime[0],self.closeTime[1],1))
        
        for i in range(2,self.length):
            #先用合并后的前两根判断走势是向上还是向下
            if chanBars[-1].high >= chanBars[-2].high:
                trend = 'up'
            else:
                trend = 'down'
            #看是否是包含关系
            if chanBars[-1].high >= self.highBar[i] and chanBars[-1].low <= self.lowBar[i]:   #前一个bar包含当前bar
                if trend == 'up':
                    chanBars[-1].low = self.lowBar[i]
                elif trend == 'down':
                    chanBars[-1].high = self.highBar[i]
                
                chanBars[-1].isMerged = True
                chanBars[-1].numOfBars += 1
                chanBars[-1].closeTime = self.closeTime[i]
                chanBars[-1].closeIndex = i
                
            elif chanBars[-1].high <= self.highBar[i] and chanBars[-1].low >= self.lowBar[i]:   #当前bar包含前一个
                if trend == 'up':
                    chanBars[-1].high = self.highBar[i]
                elif trend == 'down':
                    chanBars[-1].low = self.lowBar[i]
                
                chanBars[-1].isMerged = True
                chanBars[-1].numOfBars += 1
                chanBars[-1].closeTime = self.closeTime[i]
                chanBars[-1].closeIndex = i
            else:  #无包含关系
                chanBars.append(ChanBar(self.openBar[i],self.highBar[i],self.lowBar[i],self.closeBar[i],self.volumeBar[i],self.closeTime[i-1],self.closeTime[i],i))
        self.chanBars = chanBars
    
    def findFenxing(self):
        i = 0
        fenxings = []
        while i < len(self.chanBars)-2:
            #检验i，i+1，i+2这三根bar是否构成分型
            if self.chanBars[i+1].high > max(self.chanBars[i].high,self.chanBars[i+2].high) and self.chanBars[i+1].low > max(self.chanBars[i].low,self.chanBars[i+2].low):
                #构成顶分型
                fenxings.append(fenxing(i,i+1,i+2,'ding'))
                i += 3
            elif self.chanBars[i+1].high < min(self.chanBars[i].high,self.chanBars[i+2].high) and self.chanBars[i+1].low < min(self.chanBars[i].low,self.chanBars[i+2].low):
                #构成底分型
                fenxings.append(fenxing(i,i+1,i+2,'di'))
                i += 3
            else:
                #不构成分型
                i += 1
        self.fenxings = fenxings
        
    def findBi(self):
#         delIndex = []
#         for i in range(1,len(self.fenxings)):   
#             lastItem = self.fenxings[i-1]
#             item = self.fenxings[i]
#             if lastItem.fenxingType != item.fenxingType and (item.barIndex2 - lastItem.barIndex2)<5:
#                 delIndex.append(i)
#                 delIndex.append(i-1)
#         delIndex = set(delIndex)
#         delIndex = list(delIndex)
#         self.fenxings = [i for j, i in enumerate(self.fenxings) if j not in delIndex]
        
        #先对分型进行处理
        lastItem = self.fenxings[0]
        for item in self.fenxings[1:]:   #对拷贝进行循环
            if lastItem.fenxingType == 'ding' and item.fenxingType == 'ding' and self.chanBars[item.barIndex2].high>self.chanBars[lastItem.barIndex2].high:
                #如果两个都是顶，且这个比之前的顶高，那之前的删掉
                self.fenxings.remove(lastItem)
            elif lastItem.fenxingType == 'di' and item.fenxingType == 'di' and self.chanBars[item.barIndex2].low<self.chanBars[lastItem.barIndex2].low:
                #如果两个都是底，且这个比之前的底低，那之前的删掉
                self.fenxings.remove(lastItem)
            lastItem = item
            
    
        delIndex = []
        for i in range(1,len(self.fenxings)):   
            lastItem = self.fenxings[i-1]
            item = self.fenxings[i]
            if lastItem.fenxingType == 'ding' and item.fenxingType == 'ding' and self.chanBars[item.barIndex2].high>self.chanBars[lastItem.barIndex2].high:
                delIndex.append(i-1)
            elif lastItem.fenxingType == 'di' and item.fenxingType == 'di' and self.chanBars[item.barIndex2].low<self.chanBars[lastItem.barIndex2].low:
                delIndex.append(i-1)
        delIndex = set(delIndex)
        delIndex = list(delIndex)
        self.fenxings = [i for j, i in enumerate(self.fenxings) if j not in delIndex]
        
        delIndex = []
        for i in range(1,len(self.fenxings)):   
            lastItem = self.fenxings[i-1]
            item = self.fenxings[i]
            if lastItem.fenxingType == 'ding' and item.fenxingType == 'ding' and self.chanBars[item.barIndex2].high>self.chanBars[lastItem.barIndex2].high:
                delIndex.append(i-1)
            elif lastItem.fenxingType == 'di' and item.fenxingType == 'di' and self.chanBars[item.barIndex2].low<self.chanBars[lastItem.barIndex2].low:
                delIndex.append(i-1)
        delIndex = set(delIndex)
        delIndex = list(delIndex)
        self.fenxings = [i for j, i in enumerate(self.fenxings) if j not in delIndex]
        
        delIndex = []
        for i in range(1,len(self.fenxings)):   
            lastItem = self.fenxings[i-1]
            item = self.fenxings[i]
            if lastItem.fenxingType == 'ding' and item.fenxingType == 'ding' and self.chanBars[item.barIndex2].high>self.chanBars[lastItem.barIndex2].high:
                delIndex.append(i-1)
            elif lastItem.fenxingType == 'di' and item.fenxingType == 'di' and self.chanBars[item.barIndex2].low<self.chanBars[lastItem.barIndex2].low:
                delIndex.append(i-1)
        delIndex = set(delIndex)
        delIndex = list(delIndex)
        self.fenxings = [i for j, i in enumerate(self.fenxings) if j not in delIndex]
        
        #先对分型进行处理
        lastItem = self.fenxings[0]
        for item in self.fenxings[1:]:   #对拷贝进行循环
            if lastItem.fenxingType == 'ding' and item.fenxingType == 'ding' and self.chanBars[item.barIndex2].high>self.chanBars[lastItem.barIndex2].high:
                #如果两个都是顶，且这个比之前的顶高，那之前的删掉
                self.fenxings.remove(lastItem)
            elif lastItem.fenxingType == 'di' and item.fenxingType == 'di' and self.chanBars[item.barIndex2].low<self.chanBars[lastItem.barIndex2].low:
                #如果两个都是底，且这个比之前的底低，那之前的删掉
                self.fenxings.remove(lastItem)
            lastItem = item
        
        bis = []
        
        startType = self.fenxings[0].fenxingType
        startIndex = self.fenxings[0].barIndex2
        if startType == 'ding':
            biType = 'down'
        elif startType == 'di':
            biType = 'up'
            
        for fx in self.fenxings[1:]:
            if fx.fenxingType == startType:
                #若分型类型一样，则继续找，说明没有构成笔
                continue
            
            else:
                #分型类型不同，构成笔
                
                bis.append(bi(startIndex,fx.barIndex2,biType))
                #更新下一笔开始信息
                startType = fx.fenxingType
                startIndex = fx.barIndex2
                if startType == 'ding':
                    biType = 'down'
                elif startType == 'di':
                    biType = 'up'
                    

        #完成最后一笔
        if bis[-1].biType == 'up':
            bis.append(bi(bis[-1].barIndex2,len(self.chanBars)-1,'down'))
        else:
            bis.append(bi(bis[-1].barIndex2,len(self.chanBars)-1,'up'))
        self.bis = bis
        
    def findLines(self):
        lines = []
        
        startType = self.bis[0].biType
        startIndex = self.bis[0].barIndex1
        lineType = startType
        featureHigh = []  #线段的特征序列高点
        featureLow = []  #线段的特征序列低点
        featureHighIndex = []   #特征序列高点所在bar的index
        featureLowIndex = []    #特征序列低点所在bar的index
        featureBiIndex = []    #特征序列的bi的index
        
        i=0
        while i < len(self.bis)-1:
            #循环控制
            i+=1
            bi = self.bis[i]
            #nextBi = self.bis[i+2]
            
            if bi.biType != startType:
                #先记录2个特征序列
                if len(featureHigh)<2:
                    if bi.biType == 'up':
                        featureHigh.append(self.chanBars[bi.barIndex2].high)
                        featureHighIndex.append(bi.barIndex2)
                        featureLow.append(self.chanBars[bi.barIndex1].low)
                        featureLowIndex.append(bi.barIndex1)
                        featureBiIndex.append(i)
                    elif bi.biType == 'down':
                        featureHigh.append(self.chanBars[bi.barIndex1].high)
                        featureHighIndex.append(bi.barIndex1)
                        featureLow.append(self.chanBars[bi.barIndex2].low)
                        featureLowIndex.append(bi.barIndex2)
                        featureBiIndex.append(i)
                    continue
                
                
                if bi.biType == 'up':  #笔是向上
                    featureHigh.append(self.chanBars[bi.barIndex2].high)
                    featureHighIndex.append(bi.barIndex2)
                    featureLow.append(self.chanBars[bi.barIndex1].low)
                    featureLowIndex.append(bi.barIndex1)
                    featureBiIndex.append(i)
                    
#                    featureHigh.append(self.chanBars[nextBi.barIndex2].high)
#                    featureHighIndex.append(nextBi.barIndex2)
#                    featureLow.append(self.chanBars[nextBi.barIndex1].low)
#                    featureLowIndex.append(nextBi.barIndex1)
#                    featureBiIndex.append(i+2)
                else:
                    featureHigh.append(self.chanBars[bi.barIndex1].high)
                    featureHighIndex.append(bi.barIndex1)
                    featureLow.append(self.chanBars[bi.barIndex2].low)
                    featureLowIndex.append(bi.barIndex2)
                    featureBiIndex.append(i)
                    
#                    featureHigh.append(self.chanBars[nextBi.barIndex1].high)
#                    featureHighIndex.append(nextBi.barIndex1)
#                    featureLow.append(self.chanBars[nextBi.barIndex2].low)
#                    featureLowIndex.append(nextBi.barIndex2)
#                    featureBiIndex.append(i+2)

                
                #识别特征序列的顶分型和底分型
                if lineType == 'up':   #识别顶分型
                    if featureHigh[-2]>max(featureHigh[-1],featureHigh[-3]) and featureLow[-2]>max(featureLow[-1],featureLow[-3]):
                        #产生了顶分型，进一步看是否有缺口
                        if featureHigh[-3]>=featureLow[-2]:  #无缺口
                            #线段结束！
                            lines.append(line(startIndex,featureHighIndex[-2],lineType,featureHigh,featureLow,featureHighIndex,featureLowIndex,featureBiIndex))
                            #新线段初始化
                            i = featureBiIndex[-2]
                            startType = self.bis[i].biType
                            #startIndex = self.bis[i].barIndex1
                            startIndex = featureHighIndex[-2]
                            lineType = startType
                            featureHigh = []  #线段的特征序列高点
                            featureLow = []  #线段的特征序列低点
                            featureHighIndex = []   #特征序列高点所在bar的index
                            featureLowIndex = []    #特征序列低点所在bar的index
                            featureBiIndex = []
                            continue
                        else:  #有缺口，麻烦了我的哥
                            if i+10>=len(self.bis):
                                continue
                            nextFeaturesHigh = []
                            nextFeaturesLow = []
                            lineEndIndex = featureBiIndex[-2]
                            j = lineEndIndex + 1
                            #对下一个线段特征序列进行合并等，看是否构成分型
                            while j <= lineEndIndex + 10:
                                if len(nextFeaturesHigh) < 2:
                                    nextFeaturesHigh.append(self.chanBars[self.bis[j].barIndex2].high)
                                    nextFeaturesLow.append(self.chanBars[self.bis[j].barIndex1].low)
                                    continue
                                if nextFeaturesHigh[-1] >= nextFeaturesHigh[-2]: #特征序列向上的
                                    if self.chanBars[self.bis[j].barIndex2].high>nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex1].low<nextFeaturesLow[-1]:
                                        nextFeaturesHigh[-1] = self.chanBars[self.bis[j].barIndex2].high
                                        
                                    elif self.chanBars[self.bis[j].barIndex2].high<nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex1].low>nextFeaturesLow[-1]:
                                        nextFeaturesLow[-1] = self.chanBars[self.bis[j].barIndex1].low
                                        
                                    else:
                                        nextFeaturesHigh.append(self.chanBars[self.bis[j].barIndex2].high)
                                        nextFeaturesLow.append(self.chanBars[self.bis[j].barIndex1].low)
                                elif nextFeaturesHigh[-1] < nextFeaturesHigh[-2]: #特征序列向下的
                                    if self.chanBars[self.bis[j].barIndex2].high>nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex1].low<nextFeaturesLow[-1]:
                                        nextFeaturesLow[-1] = self.chanBars[self.bis[j].barIndex1].low
                                        
                                    elif self.chanBars[self.bis[j].barIndex2].high<nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex1].low>nextFeaturesLow[-1]:
                                        nextFeaturesHigh[-1] = self.chanBars[self.bis[j].barIndex2].high
                                    else:
                                        nextFeaturesHigh.append(self.chanBars[self.bis[j].barIndex2].high)
                                        nextFeaturesLow.append(self.chanBars[self.bis[j].barIndex1].low)
                                
                                j += 2
                                if len(nextFeaturesHigh) >= 3:
                                    if (nextFeaturesHigh[-2]<min(nextFeaturesHigh[-1],nextFeaturesHigh[-3]) and nextFeaturesLow[-2]<min(nextFeaturesLow[-1],nextFeaturesLow[-3])) or self.chanBars[self.bis[j].barIndex1].low <= self.chanBars[startIndex].low:
                                        #线段结束！
                                        lines.append(line(startIndex,featureHighIndex[-2],lineType,featureHigh,featureLow,featureHighIndex,featureLowIndex,featureBiIndex))
                                        #新线段初始化
                                        i = featureBiIndex[-2]
                                        startType = self.bis[i].biType
                                        #startIndex = self.bis[i].barIndex1
                                        startIndex = featureHighIndex[-2]
                                        lineType = startType
                                        featureHigh = []  #线段的特征序列高点
                                        featureLow = []  #线段的特征序列低点
                                        featureHighIndex = []   #特征序列高点所在bar的index
                                        featureLowIndex = []    #特征序列低点所在bar的index
                                        featureBiIndex = []
                                        break
                            continue
                            
                            
                elif lineType == 'down':   #识别底分型
                    if featureHigh[-2]<min(featureHigh[-1],featureHigh[-3]) and featureLow[-2]<min(featureLow[-1],featureLow[-3]):
                        #产生了底分型，进一步看是否有缺口
                        if featureLow[-3]<=featureHigh[-2]:  #无缺口
                            #线段结束！
                            lines.append(line(startIndex,featureLowIndex[-2],lineType,featureHigh,featureLow,featureHighIndex,featureLowIndex,featureBiIndex))
                            #新线段初始化
                            i = featureBiIndex[-2]
                            startType = self.bis[i].biType
                            #startIndex = self.bis[i].barIndex1
                            startIndex = featureLowIndex[-2]
                            lineType = startType
                            featureHigh = []  #线段的特征序列高点
                            featureLow = []  #线段的特征序列低点
                            featureHighIndex = []   #特征序列高点所在bar的index
                            featureLowIndex = []    #特征序列低点所在bar的index
                            featureBiIndex = []
                            continue
                        else:  #有缺口，麻烦了我的哥
                            if i+10>=len(self.bis):
                                continue
                            nextFeaturesHigh = []
                            nextFeaturesLow = []
                            lineEndIndex = featureBiIndex[-2]   
                            j = lineEndIndex + 1
                            #对下一个线段特征序列进行合并等，看是否构成分型
                            while j <= lineEndIndex + 10:
                                if len(nextFeaturesHigh) < 2:
                                    nextFeaturesHigh.append(self.chanBars[self.bis[j].barIndex1].high)
                                    nextFeaturesLow.append(self.chanBars[self.bis[j].barIndex2].low)
                                    continue
                                if nextFeaturesHigh[-1] >= nextFeaturesHigh[-2]: #特征序列向上的
                                    if self.chanBars[self.bis[j].barIndex1].high>nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex2].low<nextFeaturesLow[-1]:
                                        nextFeaturesHigh[-1] = self.chanBars[self.bis[j].barIndex1].high
                                        
                                    elif self.chanBars[self.bis[j].barIndex1].high<nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex2].low>nextFeaturesLow[-1]:
                                        nextFeaturesLow[-1] = self.chanBars[self.bis[j].barIndex2].low
                                        
                                    else:
                                        nextFeaturesHigh.append(self.chanBars[self.bis[j].barIndex1].high)
                                        nextFeaturesLow.append(self.chanBars[self.bis[j].barIndex2].low)
                                elif nextFeaturesHigh[-1] < nextFeaturesHigh[-2]: #特征序列向下的
                                    if self.chanBars[self.bis[j].barIndex1].high>nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex2].low<nextFeaturesLow[-1]:
                                        nextFeaturesLow[-1] = self.chanBars[self.bis[j].barIndex2].low
                                        
                                    elif self.chanBars[self.bis[j].barIndex1].high<nextFeaturesHigh[-1] and self.chanBars[self.bis[j].barIndex2].low>nextFeaturesLow[-1]:
                                        nextFeaturesHigh[-1] = self.chanBars[self.bis[j].barIndex1].high
                                    else:
                                        nextFeaturesHigh.append(self.chanBars[self.bis[j].barIndex1].high)
                                        nextFeaturesLow.append(self.chanBars[self.bis[j].barIndex2].low)
                                j += 2
                                if len(nextFeaturesHigh) >= 3:
                                    if (nextFeaturesHigh[-2]>max(nextFeaturesHigh[-1],nextFeaturesHigh[-3]) and nextFeaturesLow[-2]>max(nextFeaturesLow[-1],nextFeaturesLow[-3])) or self.chanBars[self.bis[j].barIndex1].high >= self.chanBars[startIndex].high:
                                    #线段结束！
                                        lines.append(line(startIndex,featureLowIndex[-2],lineType,featureHigh,featureLow,featureHighIndex,featureLowIndex,featureBiIndex))
                                        #新线段初始化
                                        i = featureBiIndex[-2]
                                        startType = self.bis[i].biType
                                        #startIndex = self.bis[i].barIndex1
                                        startIndex = featureLowIndex[-2]
                                        lineType = startType
                                        featureHigh = []  #线段的特征序列高点
                                        featureLow = []  #线段的特征序列低点
                                        featureHighIndex = []   #特征序列高点所在bar的index
                                        featureLowIndex = []    #特征序列低点所在bar的index
                                        featureBiIndex = []
                                        break
                            continue
                
                featureHigh.pop()
                featureHighIndex.pop()
                featureLow.pop()
                featureLowIndex.pop()
                featureBiIndex.pop()
                
#                featureHigh.pop()
#                featureHighIndex.pop()
#                featureLow.pop()
#                featureLowIndex.pop()
#                featureBiIndex.pop()
                
                #来新的特征序列，先检查是否需要合并
                if featureHigh[-1] >= featureHigh[-2]: #特征序列向上的

                    if bi.biType == 'up':  #笔是向上
                        if self.chanBars[bi.barIndex2].high>featureHigh[-1] and self.chanBars[bi.barIndex1].low<featureLow[-1]:
                            featureHigh[-1] = self.chanBars[bi.barIndex2].high
                            featureHighIndex[-1] = bi.barIndex2
                            featureBiIndex[-1] = i
                        elif self.chanBars[bi.barIndex2].high<featureHigh[-1] and self.chanBars[bi.barIndex1].low>featureLow[-1]:
                            featureLow[-1] = self.chanBars[bi.barIndex1].low
                            featureLowIndex[-1] = bi.barIndex1
                            featureBiIndex[-1] = i
                        else:
                            featureHigh.append(self.chanBars[bi.barIndex2].high)
                            featureHighIndex.append(bi.barIndex2)
                            featureLow.append(self.chanBars[bi.barIndex1].low)
                            featureLowIndex.append(bi.barIndex1)
                            featureBiIndex.append(i)
                    elif bi.biType == 'down':   #笔是向下
                        if self.chanBars[bi.barIndex1].high>featureHigh[-1] and self.chanBars[bi.barIndex2].low<featureLow[-1]:
                            featureHigh[-1] = self.chanBars[bi.barIndex1].high
                            featureHighIndex[-1] = bi.barIndex1
                            featureBiIndex[-1] = i
                        elif self.chanBars[bi.barIndex1].high<featureHigh[-1] and self.chanBars[bi.barIndex2].low>featureLow[-1]:
                            featureLow[-1] = self.chanBars[bi.barIndex2].low
                            featureLowIndex[-1] = bi.barIndex2
                            featureBiIndex[-1] = i
                        else:
                            featureHigh.append(self.chanBars[bi.barIndex1].high)
                            featureHighIndex.append(bi.barIndex1)
                            featureLow.append(self.chanBars[bi.barIndex2].low)
                            featureLowIndex.append(bi.barIndex2)
                            featureBiIndex.append(i)
                elif featureHigh[-1] < featureHigh[-2]: #特征序列向下的
                    if bi.biType == 'up':  #笔是向上
                        if self.chanBars[bi.barIndex2].high>featureHigh[-1] and self.chanBars[bi.barIndex1].low<featureLow[-1]:
                            featureLow[-1] = self.chanBars[bi.barIndex1].low
                            featureLowIndex[-1] = bi.barIndex1
                            featureBiIndex[-1] = i
                        elif self.chanBars[bi.barIndex2].high<featureHigh[-1] and self.chanBars[bi.barIndex1].low>featureLow[-1]:
                            featureHigh[-1] = self.chanBars[bi.barIndex2].high
                            featureHighIndex[-1] = bi.barIndex2
                            featureBiIndex[-1] = i
                        else:
                            featureHigh.append(self.chanBars[bi.barIndex2].high)
                            featureHighIndex.append(bi.barIndex2)
                            featureLow.append(self.chanBars[bi.barIndex1].low)
                            featureLowIndex.append(bi.barIndex1)
                            featureBiIndex.append(i)
                    elif bi.biType == 'down':   #笔是向下
                        if self.chanBars[bi.barIndex1].high>featureHigh[-1] and self.chanBars[bi.barIndex2].low<featureLow[-1]:
                            featureLow[-1] = self.chanBars[bi.barIndex2].low
                            featureLowIndex[-1] = bi.barIndex2
                            featureBiIndex[-1] = i
                        elif self.chanBars[bi.barIndex1].high<featureHigh[-1] and self.chanBars[bi.barIndex2].low>featureLow[-1]:
                            featureHigh[-1] = self.chanBars[bi.barIndex1].high
                            featureHighIndex[-1] = bi.barIndex1
                            featureBiIndex[-1] = i
                        else:
                            featureHigh.append(self.chanBars[bi.barIndex1].high)
                            featureHighIndex.append(bi.barIndex1)
                            featureLow.append(self.chanBars[bi.barIndex2].low)
                            featureLowIndex.append(bi.barIndex2)
                            featureBiIndex.append(i)
        #画完最后一根线段                    
        if featureHigh:
            lines.append(line(startIndex,self.bis[-1].barIndex2,lineType,featureHigh,featureLow,featureHighIndex,featureLowIndex,featureBiIndex))            
            
            
        #确保向上和向下正确
        i=0
        while i < len(lines):
            l = lines[i]
            
            if l.lineType == 'up' and self.chanBars[l.barIndex1].low>self.chanBars[l.barIndex2].high and i < len(lines)-1 and i != 0:
                #应该向上却没有向上
                #把三条线段变成一条
                lines[i-1].barIndex2 = lines[i+1].barIndex2
                lines.pop(i)
                lines.pop(i)
            elif l.lineType == 'down' and self.chanBars[l.barIndex1].high<self.chanBars[l.barIndex2].low and i < len(lines)-1 and i != 0:
                #应该向下却没有向下
                #把三条线段变成一条
                lines[i-1].barIndex2 = lines[i+1].barIndex2
                lines.pop(i)
                lines.pop(i)                
            i += 1
        i=0
        while i < len(lines):
            l = lines[i]
            
            if l.lineType == 'up' and self.chanBars[l.barIndex1].low>self.chanBars[l.barIndex2].high and i < len(lines)-1 and i != 0:
                #应该向上却没有向上
                #把三条线段变成一条
                lines[i-1].barIndex2 = lines[i+1].barIndex2
                lines.pop(i)
                lines.pop(i)
            elif l.lineType == 'down' and self.chanBars[l.barIndex1].high<self.chanBars[l.barIndex2].low and i < len(lines)-1 and i != 0:
                #应该向下却没有向下
                #把三条线段变成一条
                lines[i-1].barIndex2 = lines[i+1].barIndex2
                lines.pop(i)
                lines.pop(i)                
            i += 1
        i=0
        while i < len(lines):
            l = lines[i]
            
            if l.lineType == 'up' and self.chanBars[l.barIndex1].low>self.chanBars[l.barIndex2].high and i < len(lines)-1 and i != 0:
                #应该向上却没有向上
                #把三条线段变成一条
                lines[i-1].barIndex2 = lines[i+1].barIndex2
                lines.pop(i)
                lines.pop(i)
            elif l.lineType == 'down' and self.chanBars[l.barIndex1].high<self.chanBars[l.barIndex2].low and i < len(lines)-1 and i != 0:
                #应该向下却没有向下
                #把三条线段变成一条
                lines[i-1].barIndex2 = lines[i+1].barIndex2
                lines.pop(i)
                lines.pop(i)                
            i += 1
        self.lines = lines
                   
    def findZhongshus(self):
        zhongshus = []
        i = 1
        isInZhongshu = False
        linesIncluded = []
        while i<len(self.lines)-1:
            i += 1
            if isInZhongshu:
                line = self.lines[i]
                #看这笔的高低点
                if line.lineType == 'up':
                    high = self.chanBars[line.barIndex2].high
                    low = self.chanBars[line.barIndex1].low
                else:
                    high = self.chanBars[line.barIndex1].high
                    low = self.chanBars[line.barIndex2].low
                
                #看是否有重叠
                if min(upperBound,high) > max(lowerBound,low):
                    #走势中枢延伸
                    #print('走势中枢延伸')
                    linesIncluded.append(i)
                    continue
                else:
                    #走势中枢新生
                    #print('走势中枢新生')
                    isInZhongshu = False
                    linesIncluded.pop()
                    zhongshus.append(zhongshu(startIndex,self.lines[i-1].barIndex1,upperBound,lowerBound,linesIncluded))
                    linesIncluded = []
                    i+=1
            else:
                high = []
                low = []
                line1 = self.lines[i-2]
                line2 = self.lines[i-1]
                line3 = self.lines[i]
                #找高低点
                if line1.lineType == 'up':
                    high.append(self.chanBars[line1.barIndex2].high)
                    low.append(self.chanBars[line1.barIndex1].low)
                else:
                    high.append(self.chanBars[line1.barIndex1].high)
                    low.append(self.chanBars[line1.barIndex2].low)
                    
                if line2.lineType == 'up':
                    high.append(self.chanBars[line2.barIndex2].high)
                    low.append(self.chanBars[line2.barIndex1].low)
                else:
                    high.append(self.chanBars[line2.barIndex1].high)
                    low.append(self.chanBars[line2.barIndex2].low)
                    
                if line3.lineType == 'up':
                    high.append(self.chanBars[line3.barIndex2].high)
                    low.append(self.chanBars[line3.barIndex1].low)
                else:
                    high.append(self.chanBars[line3.barIndex1].high)
                    low.append(self.chanBars[line3.barIndex2].low)
                
                 #判断是否是前一个中枢的扩展
#                if len(zhongshus) > 0:
#                    if (max(high)>=zhongshus[-1].low and max(high)<=zhongshus[-1].high) or (min(low)>=zhongshus[-1].low and min(low)<=zhongshus[-1].high):
#                        #满足这个条件则是扩展
#                        upperBound = zhongshus[-1].low
#                        lowerBound = zhongshus[-1].high
#                        startIndex = zhongshus[-1].barIndex1
#                        isInZhongshu = True
#                        zhongshus.pop()
#                        
#                        #print('中枢的扩展')
                
                    
                #判断是否有重叠
                if min(high[0],high[1]) > max(low[0],low[1]):
                    #前俩有重叠
                    upperBound = min(high[0],high[1])
                    lowerBound = max(low[0],low[1])
                    if min(upperBound,high[2]) > max(lowerBound,low[2]):
                        #三个都有重叠
                        upperBound = min(upperBound,high[2])
                        lowerBound = max(lowerBound,low[2])
                        isInZhongshu = True
                        startIndex = line1.barIndex1
                        linesIncluded.append(i-2)
                        linesIncluded.append(i-1)
                        linesIncluded.append(i)
                    else:
                        continue
                else:
                    continue
                    
        if isInZhongshu:
            linesIncluded.pop()
            zhongshus.append(zhongshu(startIndex,self.lines[-1].barIndex2,upperBound,lowerBound,linesIncluded))
        self.zhongshus = zhongshus
    
    def findBiZhongshus(self):
        biZhongshus = []
        i = 1
        isInZhongshu = False
        bisIncluded = []
        while i<len(self.bis)-1:
            i += 1
            if isInZhongshu:
                bi = self.bis[i]
                #看这笔的高低点
                if bi.biType == 'up':
                    high = self.chanBars[bi.barIndex2].high
                    low = self.chanBars[bi.barIndex1].low
                else:
                    high = self.chanBars[bi.barIndex1].high
                    low = self.chanBars[bi.barIndex2].low
                
                #看是否有重叠
                if min(upperBound,high) > max(lowerBound,low):
                    #走势中枢延伸
                    #print('走势中枢延伸')
                    bisIncluded.append(i)
                    continue
                else:
                    #走势中枢新生
                    #print('走势中枢新生')
                    isInZhongshu = False
                    bisIncluded.pop()
                    biZhongshus.append(zhongshu(startIndex,self.bis[i-1].barIndex1,upperBound,lowerBound,bisIncluded))
                    bisIncluded = []
                    i+=1
            else:
                high = []
                low = []
                bi1 = self.bis[i-2]
                bi2 = self.bis[i-1]
                bi3 = self.bis[i]
                #找高低点
                if bi1.biType == 'up':
                    high.append(self.chanBars[bi1.barIndex2].high)
                    low.append(self.chanBars[bi1.barIndex1].low)
                else:
                    high.append(self.chanBars[bi1.barIndex1].high)
                    low.append(self.chanBars[bi1.barIndex2].low)
                    
                if bi2.biType == 'up':
                    high.append(self.chanBars[bi2.barIndex2].high)
                    low.append(self.chanBars[bi2.barIndex1].low)
                else:
                    high.append(self.chanBars[bi2.barIndex1].high)
                    low.append(self.chanBars[bi2.barIndex2].low)
                    
                if bi3.biType == 'up':
                    high.append(self.chanBars[bi3.barIndex2].high)
                    low.append(self.chanBars[bi3.barIndex1].low)
                else:
                    high.append(self.chanBars[bi3.barIndex1].high)
                    low.append(self.chanBars[bi3.barIndex2].low)
                
                 #判断是否是前一个中枢的扩展
#                if len(biZhongshus) > 0:
#                    if (max(high)>=biZhongshus[-1].low and max(high)<=biZhongshus[-1].high) or (min(low)>=biZhongshus[-1].low and min(low)<=biZhongshus[-1].high):
#                        #满足这个条件则是扩展
#                        upperBound = biZhongshus[-1].high
#                        lowerBound = biZhongshus[-1].low
#                        startIndex = biZhongshus[-1].barIndex1
#                        isInZhongshu = True
#                        biZhongshus.pop()
#                        
#                        #print('中枢的扩展')
                
                    
                #判断是否有重叠
                if min(high[0],high[1]) > max(low[0],low[1]):
                    #前俩有重叠
                    upperBound = min(high[0],high[1])
                    lowerBound = max(low[0],low[1])
                    if min(upperBound,high[2]) > max(lowerBound,low[2]):
                        #三个都有重叠
                        upperBound = min(upperBound,high[2])
                        lowerBound = max(lowerBound,low[2])
                        isInZhongshu = True
                        startIndex = bi1.barIndex1
                        bisIncluded.append(i-2)
                        bisIncluded.append(i-1)
                        bisIncluded.append(i)
                    else:
                        continue
                else:
                    continue
                    
        if isInZhongshu:
            bisIncluded.pop()
            biZhongshus.append(zhongshu(startIndex,self.bis[-1].barIndex2,upperBound,lowerBound,bisIncluded))
        self.biZhongshus = biZhongshus    
    
    
    def append(self,o,h,l,c,volume,time):
        self.openBar.append(o)
        self.highBar.append(h)
        self.lowBar.append(l)
        self.closeBar.append(c)
        self.volumeBar.append(volume)
        self.closeTime.append(time)
        self.length = len(self.openBar)
        
    def decision(self):
        inZhongshuLines = []
        for z in self.zhongshus:
            inZhongshuLines += z.linesIncluded
            
        qushiLines = []
        for i in range(len(self.lines)):
            if i not in inZhongshuLines and i < inZhongshuLines[-1]:
                qushiLines.append(i)
                
        nowLines = []
        for i in range(len(self.lines)):
            if i not in inZhongshuLines and i > inZhongshuLines[-1]:
                nowLines.append(i)
                
        qushiType = []        
        for i in qushiLines:
            qushiType.append(self.lines[i].lineType)
            
        #看目前是什么样的趋势
        
        if self.zhongshus[-1].high >= self.zhongshus[-2].high:
            benchmark = 'up'
        else:
            benchmark = 'down'
        
        for i in qushiLines:
            if self.bis[i].biType == benchmark:
                benchmarkLine = i
        
        
        
        
        if i > 1:  #有趋势(盘整)
            if benchmark == 'up':
                macd2 = sum(self.macd[self.chanBars[self.lines[benchmarkLine].barIndex1].closeIndex:\
                self.chanBars[self.lines[benchmarkLine].barIndex2].closeIndex])\
                /len(self.macd[self.chanBars[self.lines[benchmarkLine].barIndex1].closeIndex:\
                self.chanBars[self.lines[benchmarkLine].barIndex2].closeIndex])
                
                macd1 = sum(self.macd[self.chanBars[self.lines[qushiLines[-2]].barIndex1].closeIndex:\
                self.chanBars[self.lines[qushiLines[-2]].barIndex2].closeIndex])\
                /len(self.macd[self.chanBars[self.lines[qushiLines[-2]].barIndex1].closeIndex:\
                self.chanBars[self.lines[qushiLines[-2]].barIndex2].closeIndex])
                
                macdNow = sum(self.macd[self.chanBars[self.lines[nowLines[-1]].barIndex1].closeIndex:\
                                self.chanBars[self.lines[nowLines[-1]].barIndex2].closeIndex])\
                                /len(self.macd[self.chanBars[self.lines[nowLines[-1]].barIndex1].closeIndex:\
                                self.chanBars[self.lines[nowLines[-1]].barIndex2].closeIndex])
                
                if self.lines[nowLines[-1]].lineType == 'up' and macdNow <= macd2: #发生了背驰
                    self.dingbeichi.append(self.length)
                    
                                
                    
            elif benchmark == 'down':
                macd2 = sum(self.macd[self.chanBars[self.lines[benchmarkLine].barIndex1].closeIndex:\
                self.chanBars[self.lines[benchmarkLine].barIndex2].closeIndex])\
                /len(self.macd[self.chanBars[self.lines[benchmarkLine].barIndex1].closeIndex:\
                self.chanBars[self.lines[benchmarkLine].barIndex2].closeIndex])
                
                macd1 = sum(self.macd[self.chanBars[self.lines[qushiLines[-2]].barIndex1].closeIndex:\
                self.chanBars[self.lines[qushiLines[-2]].barIndex2].closeIndex])\
                /len(self.macd[self.chanBars[self.lines[qushiLines[-2]].barIndex1].closeIndex:\
                self.chanBars[self.lines[qushiLines[-2]].barIndex2].closeIndex])
                
                macdNow = sum(self.macd[self.chanBars[self.lines[nowLines[-1]].barIndex1].closeIndex:\
                                self.chanBars[self.lines[nowLines[-1]].barIndex2].closeIndex])\
                                /len(self.macd[self.chanBars[self.lines[nowLines[-1]].barIndex1].closeIndex:\
                                self.chanBars[self.lines[nowLines[-1]].barIndex2].closeIndex])
                
                if self.lines[nowLines[-1]].lineType == 'down' and macdNow >= macd2: #发生了背驰
                    self.dibeichi.append(self.length)
                    
    
                
    def decisionBi(self):
        inZhongshuLines = []
        for z in self.biZhongshus:
            inZhongshuLines += z.linesIncluded
            
        qushiLines = list(range(self.biZhongshus[-2].linesIncluded[-1]+1,self.biZhongshus[-1].linesIncluded[0]))
        qushiLinesLast = list(range(self.biZhongshus[-3].linesIncluded[-1]+1,self.biZhongshus[-2].linesIncluded[0]))
        
                
        nowLines = []
        for i in range(len(self.bis)):
            if i not in inZhongshuLines and i > inZhongshuLines[-1]:
                nowLines.append(i)
                
           
        #看目前是什么样的趋势
        
        if self.biZhongshus[-1].high >= self.biZhongshus[-2].high:
            benchmark = 'up'
        else:
            benchmark = 'down'
        
        for i in qushiLines:
            if self.bis[i].biType == benchmark:
                benchmarkLine = i
                
        #看趋势是否延续一段时间
        if self.biZhongshus[-2].high >= self.biZhongshus[-3].high:
            if benchmark =='up':
                lastingTrend = 'up'
            else:
                lastingTrend = 'none'
        else:
            if benchmark == 'down':
                lastingTrend = 'down'
            else:
                lastingTrend = 'none'
                
        for i in qushiLinesLast:
            if self.bis[i].biType == benchmark:
                benchmarkLineLast = i
        
#        #找benchmark趋势段macd情况
#        try:
#            macdBenchmark, macdBenchmarkStart, macdBenchmarkEnd = self.matchMacd(benchmarkLine)    
#        except:
#            macdBenchmark = 0
#                
#        #找benchmarkLast趋势段macd情况
#        try:
#            macdBenchmarkLast, macdBenchmarkLastStart, macdBenchmarkLastEnd = self.matchMacd(benchmarkLineLast)
#        except:
#            macdBenchmarkLast = 0
        #找benchmark趋势段macd情况
        try:
            
            #找趋势背驰
        
            if lastingTrend != 'none':
                
                macdBenchmark, macdBenchmarkStart, macdBenchmarkEnd = self.matchMacd(benchmarkLine)
                macdBenchmarkLast, macdBenchmarkLastStart, macdBenchmarkLastEnd = self.matchMacd(benchmarkLineLast)
                
                if lastingTrend == 'up':
                    #判断是否创新高
                    benchmarkLineHigh = self.chanBars[self.bis[benchmarkLine].barIndex2].high
                    benchmarkLineLastHigh = self.chanBars[self.bis[benchmarkLineLast].barIndex2].high
                    #判断是否背驰
                    if benchmarkLineHigh >= benchmarkLineLastHigh and macdBenchmark <= macdBenchmarkLast and macdBenchmark!=0 and macdBenchmarkLast!=0:
                        self.trendDingbeichi.append(self.length)
                        self.macdBenchmarkStart.append(macdBenchmarkStart)
                        self.macdBenchmarkEnd.append(macdBenchmarkEnd)
                        self.macdBenchmarkLastStart.append(macdBenchmarkLastStart)
                        self.macdBenchmarkLastEnd.append(macdBenchmarkLastEnd)
                elif lastingTrend == 'down':
                    #判断是否创新低                
                    benchmarkLineLow = self.chanBars[self.bis[benchmarkLine].barIndex2].low
                    benchmarkLineLastLow = self.chanBars[self.bis[benchmarkLineLast].barIndex2].low
                    #判断是否背驰
                    if benchmarkLineLow <= benchmarkLineLastLow and macdBenchmark >= macdBenchmarkLast and macdBenchmark!=0 and macdBenchmarkLast!=0:
                        self.trendDibeichi.append(self.length)
                        self.macdBenchmarkStart.append(macdBenchmarkStart)
                        self.macdBenchmarkEnd.append(macdBenchmarkEnd)
                        self.macdBenchmarkLastStart.append(macdBenchmarkLastStart)
                        self.macdBenchmarkLastEnd.append(macdBenchmarkLastEnd)
        except:
            pass
        
        
        
       #找盘整背驰
        try:
           macdNow, macdNowStart, macdNowEnd = self.matchMacd(nowLine)

           if benchmark == 'up' and self.bis[nowLine].biType == 'up' and (self.chanBars[self.bis[nowLine].barIndex2].closeIndex - self.chanBars[self.bis[nowLine].barIndex1].closeIndex) > 3:
               
               
               #判断是否创新高
               benchmarkLineHigh = self.chanBars[self.bis[benchmarkLine].barIndex2].high
               
               
               if macdNow <= macdBenchmark and self.highBar[-1] >= benchmarkLineHigh: #发生了背驰
                   self.dingbeichi.append(self.length)
                   if self.position == 0:
                       self.dingbeichiLine.append(nowLine)
                   
                                                   
           elif benchmark == 'down' and self.bis[nowLine].biType == 'down' and (self.chanBars[self.bis[nowLine].barIndex2].closeIndex - self.chanBars[self.bis[nowLine].barIndex1].closeIndex) > 3:
               
               #判断是否创新低
               benchmarkLineLow = self.chanBars[self.bis[benchmarkLine].barIndex2].low            
               
               if macdNow >= macdBenchmark and self.lowBar[-1] <= benchmarkLineLow: #发生了背驰
                   self.dibeichi.append(self.length)
                   if self.position == 0:
                       self.dibeichiLine.append(nowLine)
                   
        except:
           pass
       
       #check 是否开仓
        try:
           if self.position == 0:
               if nowLine == self.dibeichiLine[-1]+1:
                   self.position = 1
                   self.openLong.append(self.length)
               elif nowLine == self.dingbeichiLine[-1]+1:
                   self.position = -1
                   self.openShort.append(self.length)
                   
           if self.position == 1:
               if nowLine == self.dibeichiLine[-1]+2:
                   self.position = 0
                   self.closeLong.append(self.length)
                   
           if self.position == -1:
               if nowLine == self.dingbeichiLine[-1]+2:
                   self.position = 0
                   self.closeShort.append(self.length)
        except:
           pass
                                               
    
    def macdSeparate(self):
        breakpoint = []
        for i in range(self.length):
            
            if i>13 and self.macd[i] * self.macd[i-1] < 0: #macd柱子穿越0轴
                breakpoint.append(i)
        self.breakpoint = breakpoint
        
    def nowTrend(self):
        if self.biZhongshus[-1].high >= self.biZhongshus[-2].high:
            trend = 'up'
        else:
            trend = 'down'
            
        if self.biZhongshus[-2].high >= self.biZhongshus[-3].high:

            lastingTrend = 'up'
        else:
            
            lastingTrend = 'down'
            
    def matchMacd(self,line):
        lineStart = self.chanBars[self.bis[line].barIndex1].closeIndex
        lineEnd = self.chanBars[self.bis[line].barIndex2].closeIndex
        macdPeriodStart = bisect.bisect(self.breakpoint,lineStart) - 1
        macdPeriodEnd = bisect.bisect(self.breakpoint,lineEnd) + 1
        
        macdBenchmark = 0
        if macdPeriodStart < 0:
            macdPeriodStart = 0
        macdPeriod = self.breakpoint[macdPeriodStart:macdPeriodEnd]
        
        if len(macdPeriod) <= 1:
            return 0,0,0
        for i in range(0,len(macdPeriod)-1):
            
            macdTemp = self.macd[macdPeriod[i]:macdPeriod[i+1]]
            if macdTemp[0] > 0:               
                macdTemp = max(macdTemp)
            else:
                macdTemp = min(macdTemp)
            if np.abs(self.diff[macdPeriod[i]])<500:
                if macdTemp < 0 and self.bis[line].biType == 'down' and macdTemp < macdBenchmark:
                    macdBenchmark = macdTemp
                elif macdTemp > 0 and self.bis[line].biType == 'up'and macdTemp > macdBenchmark:
                    macdBenchmark = macdTemp
            #macdBenchmark = macdTemp
        macdBenchmarkStart = macdPeriod[i]
        macdBenchmarkEnd = macdPeriod[i+1]
        return macdBenchmark, macdBenchmarkStart, macdBenchmarkEnd
        
    def matchMacd2(self,line):
        lineStart = self.chanBars[self.bis[line].barIndex1].closeIndex
        lineEnd = self.chanBars[self.bis[line].barIndex2].closeIndex
        if self.bis[line].biType == 'up':
            return max(self.macd[lineStart:lineEnd])
        else:
            return min(self.macd[lineStart:lineEnd])
    
    def findTrendLines(self):
        
        
        for i in range(len(self.biZhongshus)-1):
            trendLines = list(range(self.biZhongshus[i].linesIncluded[-1]+1,self.biZhongshus[i+1].linesIncluded[0]))
            if self.biZhongshus[i+1].high >= self.biZhongshus[i].high:  #向上的中枢
                for line in trendLines:
                    if self.bis[line].biType == 'up':
                        self.trendLineRecord.append(line)
            else:  #向下的中枢
                for line in trendLines:
                    if self.bis[line].biType == 'down':
                        self.trendLineRecord.append(line)
        
        #self.trendLineRecord = list(range(len(self.bis)))
                        
        self.trendLineMacd = []
        for line in self.trendLineRecord:
            lineMacd,start,end = self.matchMacd(line)
            self.trendLineMacd.append(lineMacd)
    
    
    def combineMacd(self,startIndex,endIndex):
        realClose = self.closeBar[startIndex:endIndex]
        simu = [realClose[0] for i in range(26)]
        close = simu+realClose
        emaslow, emafast, diff = moving_average_convergence(close)
        dea = moving_average(diff, 9, type='exponential')
        macd = diff - dea
            
       
        return np.mean(macd[26:])
            
            
    def calculateCombinedMacd(self):
        self.trendLineMacd = []
        for line in self.trendLineRecord:
            if chan.chanBars[chan.bis[line].barIndex2].closeIndex - chan.chanBars[chan.bis[line].barIndex1].closeIndex >1:
                self.trendLineMacd.append(self.combineMacd(chan.chanBars[chan.bis[line].barIndex1].closeIndex,chan.chanBars[chan.bis[line].barIndex2].closeIndex))
            else:
                self.trendLineMacd.append(0)
            