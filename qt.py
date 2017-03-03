# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:06:35 2017

@author: lizard
"""


import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import pickle
from chan import Chan
import numpy as np
import math
import time
#from feedData import feedData
#from feedData import nowTime
import threading
from pandas import DataFrame
import matplotlib.pyplot as plt


# Create a subclass of GraphicsObject.
# The only required methods are paint() and boundingRect()
# (see QGraphicsItem documentation)


class CandlestickItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.flagHasData = False

    def set_data(self, data):
        self.data = data  # data must have fields: time, open, close, min, max
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def generatePicture(self):
        # pre-computing a QPicture object allows paint() to run much more quickly,
        # rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setBrush(pg.mkBrush('r'))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
        p.end()

    def paint(self, p, *args):
        if self.flagHasData:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())


class BisItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.flagHasData = False

    def set_data(self, data):
        self.data = data  # data must have fields: time, open, close, min, max
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def generatePicture(self):
        # pre-computing a QPicture object allows paint() to run much more quickly,
        # rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)

        for bi in self.data:
            if bi.biType == 'up':
                p.setPen(pg.mkPen('r'))
                p.drawLine(QtCore.QPointF(chan.chanBars[bi.barIndex1].closeIndex, chan.lowBar[chan.chanBars[bi.barIndex1].closeIndex]), QtCore.QPointF(
                    chan.chanBars[bi.barIndex2].closeIndex, chan.highBar[chan.chanBars[bi.barIndex2].closeIndex]))
            else:
                p.setPen(pg.mkPen('g'))
                p.drawLine(QtCore.QPointF(chan.chanBars[bi.barIndex1].closeIndex, chan.highBar[chan.chanBars[bi.barIndex1].closeIndex]), QtCore.QPointF(
                    chan.chanBars[bi.barIndex2].closeIndex, chan.lowBar[chan.chanBars[bi.barIndex2].closeIndex]))
        p.end()

    def paint(self, p, *args):
        if self.flagHasData:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())


class LinesItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.flagHasData = False

    def set_data(self, data):
        self.data = data  # data must have fields: time, open, close, min, max
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def generatePicture(self):
        # pre-computing a QPicture object allows paint() to run much more quickly,
        # rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)

        for line in self.data:
            if line.lineType == 'up':
                p.setPen(pg.mkPen('r'))
                p.drawLine(QtCore.QPointF(chan.chanBars[line.barIndex1].closeIndex, chan.lowBar[chan.chanBars[line.barIndex1].closeIndex]), QtCore.QPointF(
                    chan.chanBars[line.barIndex2].closeIndex, chan.highBar[chan.chanBars[line.barIndex2].closeIndex]))
            else:
                p.setPen(pg.mkPen('g'))
                p.drawLine(QtCore.QPointF(chan.chanBars[line.barIndex1].closeIndex, chan.highBar[chan.chanBars[line.barIndex1].closeIndex]), QtCore.QPointF(
                    chan.chanBars[line.barIndex2].closeIndex, chan.lowBar[chan.chanBars[line.barIndex2].closeIndex]))
        p.end()

    def paint(self, p, *args):
        if self.flagHasData:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())


class ZhongshusItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.flagHasData = False

    def set_data(self, data):
        self.data = data  # data must have fields: time, open, close, min, max
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def generatePicture(self):
        # pre-computing a QPicture object allows paint() to run much more quickly,
        # rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        p.setBrush(pg.mkBrush(None))
        for zhongshu in self.data:
            p.drawRect(QtCore.QRectF(chan.chanBars[zhongshu.barIndex1].closeIndex,
                                     zhongshu.low, chan.chanBars[
                                         zhongshu.barIndex2].closeIndex - chan.chanBars[zhongshu.barIndex1].closeIndex,
                                     zhongshu.high - zhongshu.low))
        p.end()

    def paint(self, p, *args):
        if self.flagHasData:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())

class DateAxis(pg.AxisItem):
    def __init__(self, dates, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.x_values = list(range(len(dates)))
#        self.x_strings = []
#        for i in dates:
#            self.x_strings.append(i.strftime('%Y%m%d'))
        self.x_strings = dates
        
    def tickStrings(self, values, scale, spacing):
        strings = []
        if(len(values)==0):
            return strings
        rng = max(values)-min(values)
        for v in values:
            vs = v* scale
            if vs in self.x_values:
                if rng >= 100:
                    
                    vstr = self.x_strings[np.abs(self.x_values-vs).argmin()].strftime('%Y%m%d')
                else:
                    vstr = self.x_strings[np.abs(self.x_values-vs).argmin()].strftime('%Y%m%d,%H:%M')
            else:
                vstr = ""
            strings.append(vstr)         
        return strings

global data
import sys
sys.path.append('./')
sys.path.append('../')
import pandas as pd

class ValuesParser:
    def __init__(self,dataframe):
        self.Data = [data['open'].tolist(),data['high'].tolist(),data['low'].tolist(),data['close'].tolist(),data['volume'].tolist()]
        self.Times= data.index.values.tolist()


data = pd.DataFrame.from_csv('rb1705_year.csv')[10000:11500]
data = ValuesParser(data)

global dataToNow
#dataToNow = w.wst(code, "last", data.Times[-1], nowTime, "")
dataToNow = []
    
    
quotes = []
for i in range(len(data.Times)):
    quotes.append([i, data.Data[0][i], data.Data[3][i],
                   data.Data[2][i], data.Data[1][i]])
    
global chan
#chan = Chan(data.Data[0], data.Data[1], data.Data[2],data.Data[3], data.Data[4], data.Times)
chan = Chan([],[],[],[],[],[])

print(len(data.Times))
start = 400
for tick in range(0, start):
    chan.append(data.Data[0][tick], data.Data[1][tick], data.Data[2][tick], data.Data[3][tick], data.Data[4][tick], data.Times[tick])
 

for tick in range(start, len(data.Times)):
    chan.append(data.Data[0][tick], data.Data[1][tick], data.Data[2][tick], data.Data[3][tick], data.Data[4][tick], data.Times[tick])
    chan.barsMerge()
    chan.findFenxing()
    chan.findBi()
    chan.findLines()
    chan.findZhongshus()
    chan.calculate_ta()
    chan.findBiZhongshus()
    chan.macdSeparate()
    chan.findTrendLines()
    chan.decisionBi()

    
#chan.plotBuySell()
chan.plotBeichi()
plt.show()
print(len(chan.dingbeichi))

        
# app = QtGui.QApplication([])
# win = pg.GraphicsWindow()
# win.setWindowTitle('行情+缠论')
# label = pg.LabelItem(justify = "center")
# win.addItem(label)
# axis = DateAxis(data.Times,orientation='bottom')
# p1 = win.addPlot(row=1, col=0,axisItems = {'bottom':axis})
# p2 = win.addPlot(row=2, col=0,axisItems = {'bottom':axis})
# p2.setXLink(p1)
# p2.plot(x = list(range(len(data.Times))),y = chan.diff,pen = 'w')
# p2.plot(x = list(range(len(data.Times))),y = chan.dea,pen = 'y')
# hLine = pg.InfiniteLine(angle=0, movable=False)
# hLine.setPos(0)
# p2.addItem(hLine, ignoreBounds=True)
# macdPositive = []
# macdNegetive = []
# for i in chan.macd:
#     if i>=0:
#         macdPositive.append(i)
#         macdNegetive.append(0)
#     else:
#         macdPositive.append(0)
#         macdNegetive.append(i)
        
# curve0 = p2.plot(x = list(range(len(data.Times))),y = np.zeros(len(data.Times)))
# curve1 = p2.plot(x = list(range(len(data.Times))),y = macdPositive, pen = 'w')
# curve2 = p2.plot(x = list(range(len(data.Times))),y = macdNegetive, pen = 'w')
# itemFill1 = pg.FillBetweenItem(curve0,curve1,pg.mkBrush('r'))
# itemFill2 = pg.FillBetweenItem(curve0,curve2,pg.mkBrush('g'))
# p2.addItem(itemFill1)
# p2.addItem(itemFill2)

# #win.addItem(label)
# #text = pg.TextItem('test',anchor=(0,1))
# # p1.addItem(text)




# itemK = CandlestickItem()
# itemK.set_data(quotes)
# itemBi = BisItem()
# itemBi.set_data(chan.bis)
# itemLine = LinesItem()
# itemLine.set_data(chan.lines)
# itemZhongshu = ZhongshusItem()
# #itemZhongshu.set_data(chan.zhongshus)
# itemZhongshu.set_data(chan.biZhongshus)

# p1.plot()
# p1.addItem(itemK)
# p1.addItem(itemBi)
# p1.addItem(itemLine)
# p1.addItem(itemZhongshu)
# p1.showGrid(x=True,y=True)

# #p1.setWindowTitle('pyqtgraph example: customGraphicsItem')

# # cross hair
# vLine = pg.InfiniteLine(angle=90, movable=False)
# hLine = pg.InfiniteLine(angle=0, movable=False)
# p1.addItem(vLine, ignoreBounds=True)
# p1.addItem(hLine, ignoreBounds=True)


# vb1 = p1.vb
# vb2 = p2.vb

# def mouseMoved(evt):
#     pos = evt[0]  # using signal proxy turns original arguments into a tuple
    
#     if p1.sceneBoundingRect().contains(pos):
#         mousePoint = vb1.mapSceneToView(pos)
#         index = int(mousePoint.x())
#         if index > 0 and index < len(quotes):
#             label.setText("<span style='font-size: 12pt'>date=%s,   <span style='color: red'>open=%0.01f</span>,   <span style='color: green'>close=%0.01f\n, high = %0.01f, low = %0.01f</span>" %
#                           (data.Times[index].strftime('%Y%m%d,%H:%M'), quotes[index][1], quotes[index][2], quotes[index][3], quotes[index][4]))
#         vLine.setPos(mousePoint.x())
#         hLine.setPos(mousePoint.y())
#     setYRange()
    
    
# def setYRange():
#     r = vb1.viewRange()
#     xmin = math.floor(r[0][0])
#     xmax = math.ceil(r[0][1])

#     #fix index <0 bug
#     xmax = max(0,xmax-xmin)
#     xmin = max(0,xmin)

#     xmin = min(xmin,len(data.Times)-1)
#     xmax = min(xmax,len(data.Times)-1)

#     highBound1 = max(data.Data[1][xmin:xmax])
#     lowBound1 = min(data.Data[2][xmin:xmax])
#     p1.setRange(yRange=(lowBound1,highBound1))
#     highBound2 = max(chan.diff[xmin:xmax])
#     lowBound2 = min(chan.diff[xmin:xmax])
#     p2.setRange(yRange=(lowBound2,highBound2))

# proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

# aaa = 0
# def update():
#     global itemK,itemBi,itemLine,itemZhongshu
#     dataToNowDf = DataFrame(index=dataToNow.Times,data = dataToNow.Data[0],columns=['price'])
#     dataToNowDf = dataToNowDf.between_time('9:30','11:30').append(dataToNowDf.between_time('13:00','15:00'))
#     a = dataToNowDf.resample('30T',how = {'price':'ohlc'},label='right').dropna()
#     for i in a.iterrows():
#         data.Times.append(i[0].to_datetime())
#         data.Data[0].append(i[1]['price']['open'])
#         data.Data[1].append(i[1]['price']['high'])
#         data.Data[2].append(i[1]['price']['low'])
#         data.Data[3].append(i[1]['price']['close'])
#         data.Data[4].append(0)
#     quotes = []
#     for i in range(len(data.Times)):
#         quotes.append([i, data.Data[0][i], data.Data[3][i],
#                        data.Data[2][i], data.Data[1][i]])
     
#     chan = Chan(data.Data[0], data.Data[1], data.Data[2],
#                 data.Data[3], data.Data[4], data.Times)
#     chan.barsMerge()
#     chan.findFenxing()
#     chan.findBi()
#     chan.findLines()
#     chan.findZhongshus()
#     chan.calculate_ta()
#     a += 1
#     itemK.set_data(quotes)
# #    itemBi.set_data(chan.bis)
# #    itemLine.set_data(chan.lines)
# #    itemZhongshu.set_data(chan.zhongshus)
#     app.processEvents()  ## force complete redraw for every plot
    
# #timer = QtCore.QTimer()
# #timer.timeout.connect(update)
# #timer.start(100000)

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        threadFeedData = threading.Thread(target=feedData, name='threadFeedData')
#        threadFeedData.start()
#        threadFeedData.join()
        QtGui.QApplication.instance().exec_()

        