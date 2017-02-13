# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 10:47:46 2017

@author: lizard
"""

from chan import *
from WindPy import *
import pickle


class chanAnalysis(object):
    def __init__(self, code, startTime, endTime):
        #w.start()
        # self.data1m = w.wsi("000001.SH", "open,high,low,close,volume",
        #                     "2012-01-01 09:00:00", "2017-01-01 15:30:00", "BarSize=1")
        # self.data5m = w.wsi(code, "open,high,low,close,volume",
        #                     "2014-01-01 09:00:00", "2017-01-01 15:30:00", "BarSize=5;PriceAdj=F")
        # self.data30m = w.wsi(code, "open,high,low,close,volume",
        #                      "2014-01-01 09:00:00", "2017-01-01 15:30:00", "BarSize=30;PriceAdj=F")
        self.data30m = pickle.load(
            open(r'C:\Users\lizard\Desktop\chan\创业板30分K\%s.pkl' % code, 'rb'))
        # self.dataDay = w.wsd(code, "open,high,low,close,volume",
        #                      "2014-01-01", "2017-01-01", "PriceAdj=F")
        self.dataDay = pickle.load(
            open(r'C:\Users\lizard\Desktop\chan\创业板日K\%s.pkl' % code, 'rb'))
        # self.dataWeek = w.wsd(code, "open,high,low,close,volume",
        #                       "2014-01-01", "2017-01-01", "Period=W;PriceAdj=F")

        # self.chan5m = Chan(self.data5m.Data[0], self.data5m.Data[1], self.data5m.Data[
        # 2], self.data5m.Data[3], self.data5m.Data[4], self.data5m.Times)
        self.chan30m = Chan(self.data30m.Data[0], self.data30m.Data[1], self.data30m.Data[
                            2], self.data30m.Data[3], self.data30m.Data[4], self.data30m.Times)
        self.chanDay = Chan(self.dataDay.Data[0], self.dataDay.Data[1], self.dataDay.Data[
                            2], self.dataDay.Data[3], self.dataDay.Data[4], self.dataDay.Times)
        # self.chanWeek = Chan(self.dataWeek.Data[0], self.dataWeek.Data[1], self.dataWeek.Data[
        # 2], self.dataWeek.Data[3], self.dataWeek.Data[4],
        # self.dataWeek.Times)

        self.zhongshus5m = []
        self.zhongshus30m = []
        self.zhongshusDay = []
        self.zhongshusWeek = []

        self.code = code

    def analysis(self):

        # self.chan5m.barsMerge()
        # self.chan5m.findFenxing()
        # self.chan5m.findBi()
        # self.chan5m.findLines()
        # self.chan5m.findZhongshus()
        # self.chan5m.findBiZhongshus()
        # self.chan5m.calculate_ta()

        self.chan30m.barsMerge()
        self.chan30m.findFenxing()
        self.chan30m.findBi()
        self.chan30m.findLines()
        self.chan30m.findZhongshus()
        self.chan30m.findBiZhongshus()
        self.chan30m.calculate_ta()

        self.chanDay.barsMerge()
        self.chanDay.findFenxing()
        self.chanDay.findBi()
        self.chanDay.findLines()
        self.chanDay.findZhongshus()
        self.chanDay.findBiZhongshus()
        self.chanDay.calculate_ta()

        # self.chanWeek.barsMerge()
        # self.chanWeek.findFenxing()
        # self.chanWeek.findBi()
        # self.chanWeek.findLines()
        # self.chanWeek.findZhongshus()
        # self.chanWeek.findBiZhongshus()
        # self.chanWeek.calculate_ta()

        # for zhongshu in self.chan5m.zhongshus:
        #     self.zhongshus5m.append((self.chan5m.chanBars[zhongshu.barIndex1].startTime, self.chan5m.chanBars[
        # zhongshu.barIndex2].closeTime, zhongshu.high, zhongshu.low))

        for zhongshu in self.chan30m.zhongshus:
            self.zhongshus30m.append((self.chan30m.chanBars[zhongshu.barIndex1].startTime, self.chan30m.chanBars[
                                     zhongshu.barIndex2].closeTime, zhongshu.high, zhongshu.low))

        for zhongshu in self.chanDay.zhongshus:
            self.zhongshusDay.append((self.chanDay.chanBars[zhongshu.barIndex1].startTime, self.chanDay.chanBars[
                                     zhongshu.barIndex2].closeTime, zhongshu.high, zhongshu.low))

        # for zhongshu in self.chanWeek.zhongshus:
        #     self.zhongshusWeek.append((self.chanWeek.chanBars[zhongshu.barIndex1].startTime, self.chanWeek.chanBars[
        # zhongshu.barIndex2].closeTime, zhongshu.high, zhongshu.low))
