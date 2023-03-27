from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import numpy as np


class wellInfoWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self, buttonNr, plateNr, plateInfo, framerate):
        super().__init__()
        self.setWindowTitle('Well Information')

        self.wellInformation = {}
        self.framerate = framerate
        self.getInfos(buttonNr, plateNr, plateInfo)
        self.createPlot()

        self.mainLayout = QHBoxLayout()
        self.textLayout = QVBoxLayout()

        headlineStr = 'Well ' + str(buttonNr) + ' on Plate ' + str(plateNr + 1)
        headlineLabel = QLabel(headlineStr)
        headlineLabel.setAlignment(Qt.AlignLeft)
        headlineLabel.setStyleSheet('font-size: 25pt; font-weight: bold;')
        self.textLayout.addWidget(headlineLabel)

        self.addStepInfo()
        self.textLayout.addWidget(self.scrollArea)
        #self.textLayout.addStretch()
        self.mainLayout.addLayout(self.textLayout)
        self.mainLayout.addWidget(self.graphWidget)
        self.setLayout(self.mainLayout)

    def getInfos(self, buttonNr, plateNr, plateInfo):
        well = 'Button_' + str(buttonNr)
        
        for step in plateInfo:
            self.wellInformation['Step ' + str(step)] = {'Length': plateInfo[step][0]}
            if plateNr == 0:
                try:
                    self.wellInformation['Step ' + str(step)]['Well Info'] = plateInfo[step][1]['Plate 1 Wells'][well]
                except:
                    self.wellInformation['Step ' + str(step)]['Well Info'] = None
            elif plateNr == 1:
                try:
                    self.wellInformation['Step ' + str(step)]['Well Info'] = plateInfo[step][1]['Plate 2 Wells'][well]
                except:
                    self.wellInformation['Step ' + str(step)]['Well Info'] = None

    def addStepInfo(self):

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumWidth(280)
        scrollAreaWidget = QWidget()
        scrollAreaWidgetLayout = QVBoxLayout()
        scrollAreaWidgetLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        for step in self.wellInformation:
            formLayout = QGridLayout()
            wellinfo = self.wellInformation[step]['Well Info']

            stepName = QLabel(step)
            stepName.setAlignment(Qt.AlignLeft)
            stepName.setStyleSheet('font-weight: bold;')
            count = scrollAreaWidgetLayout.count() - 1
            scrollAreaWidgetLayout.insertWidget(count, stepName)

            stepLengthH = str(self.wellInformation[step]['Length'][0])
            if len(stepLengthH) < 2:
                stepLengthH = '0' + stepLengthH
            stepLengthM = str(self.wellInformation[step]['Length'][1])
            if len(stepLengthM) < 2:
                stepLengthM = '0' + stepLengthM
            stepLengthS = str(self.wellInformation[step]['Length'][2])
            if len(stepLengthS) < 2:
                stepLengthS = '0' + stepLengthS
            stepLength = str(stepLengthH) + ':' + str(stepLengthM) + ':' + str(stepLengthS)
            formLayout.addWidget(QLabel('Step length:'), 0, 0, 1, 1)
            formLayout.addWidget(QLabel(stepLength), 0, 1, 1, 1)

            if wellinfo is None:
                formLayout.addWidget(QLabel('Well not used.'), 1, 0, 1, 1)
            else:
                formLayout.addWidget(QLabel('Color:'), 1, 0, 1, 1)
                formLayout.addWidget(QLabel(wellinfo['color']), 1, 1, 1, 1)

                if wellinfo['waveType'] in {'sin', 'tri', 'sq', 'pwm', 'rise', 'fall'}:
                    if wellinfo['waveType'] == 'sin':
                        formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                        formLayout.addWidget(QLabel('Sine Wave'), 2, 1, 1, 1)
                    elif wellinfo['waveType'] == 'tri':
                        formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                        formLayout.addWidget(QLabel('Triangle wave'), 2, 1, 1, 1)
                    elif wellinfo['waveType'] == 'sq':
                        formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                        formLayout.addWidget(QLabel('Square Wave'), 2, 1, 1, 1)
                    elif wellinfo['waveType'] == 'pwm':
                        formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                        formLayout.addWidget(QLabel('PWM'), 2, 1, 1, 1)
                    elif wellinfo['waveType'] == 'rise':
                        formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                        formLayout.addWidget(QLabel('Rise'), 2, 1, 1, 1)
                    elif wellinfo['waveType'] == 'fall':
                        formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                        formLayout.addWidget(QLabel('Fall'), 2, 1, 1, 1)
                    if wellinfo['waveType'] != 'pwm':
                        formLayout.addWidget(QLabel('Maximum Intensity:'), 3, 0, 1, 1)
                        formLayout.addWidget(QLabel(str(wellinfo['maxVal'])), 3, 1, 1, 1)
                        formLayout.addWidget(QLabel('Minimum Intensity:'), 4, 0, 1, 1)
                        formLayout.addWidget(QLabel(str(wellinfo['minVal'])), 4, 1, 1, 1)
                        if wellinfo['waveType'] not in {'rise', 'fall'}:
                            formLayout.addWidget(QLabel('Wavelength:'), 5, 0, 1, 1)
                            formLayout.addWidget(QLabel(str(wellinfo['wvLen'])), 5, 1, 1, 1)
                    else:
                        formLayout.addWidget(QLabel('Intensity:'), 3, 0, 1, 1)
                        formLayout.addWidget(QLabel(str(wellinfo['maxVal'])), 3, 1, 1, 1)
                        formLayout.addWidget(QLabel('Duty cycle:'), 4, 0, 1, 1)
                        formLayout.addWidget(QLabel(str(wellinfo['dutyCyclePWM']) + ' %'), 4, 1, 1, 1)
                        formLayout.addWidget(QLabel('Period:'), 5, 0, 1, 1)
                        formLayout.addWidget(QLabel(str(wellinfo['periodPWM']) + ' min'), 5, 1, 1, 1)
                    if wellinfo['waveType'] not in {'rise', 'fall'}:
                        formLayout.addWidget(QLabel('Start position:'), 6, 0, 1, 1)
                        formLayout.addWidget(QLabel(wellinfo['start']), 6, 1, 1, 1)
                else:
                    formLayout.addWidget(QLabel('Type:'), 2, 0, 1, 1)
                    formLayout.addWidget(QLabel('None'), 2, 1, 1, 1)
                    formLayout.addWidget(QLabel('Intensity:'), 3, 0, 1, 1)
                    formLayout.addWidget(QLabel(str(wellinfo['maxVal'])), 3, 1, 1, 1)

            count = scrollAreaWidgetLayout.count() - 1
            scrollAreaWidgetLayout.insertLayout(count, formLayout)

            scrollAreaWidget.setLayout(scrollAreaWidgetLayout)
            self.scrollArea.setWidget(scrollAreaWidget)

    def createPlot(self):
        self.graphWidget = pg.PlotWidget()
        self.pen = pg.mkPen(color='red', width=2)

        self.graphWidget.setBackground('w')
        labelStyle = {'color': 'black', 'font-size': '12pt'}
        self.graphWidget.setLabel('bottom', "Time / min", **labelStyle)
        self.graphWidget.setLabel('left', "Intensity", **labelStyle)

        programmLen = 0
        firstStep = True

        for step in self.wellInformation:

            wellinfo = self.wellInformation[step]['Well Info']
            stepLength = self.wellInformation[step]['Length'][0] * 60 + \
             self.wellInformation[step]['Length'][1] + self.wellInformation[step]['Length'][2] / 60 + self.framerate

            if wellinfo is None:
                programmLen += stepLength - self.framerate
                firstStep = True
            else:

                wvType = wellinfo['waveType']
                wvMax = wellinfo['maxVal']

                if wvType not in {'pwm', 'const'}:
                    wvMin = wellinfo['minVal']
                    if wvType not in {'rise', 'fall'}:
                        wvLen = wellinfo['wvLen']
                elif wvType == 'pwm':
                    dutyCyclePWM = wellinfo['dutyCyclePWM']
                    periodPWM = wellinfo['periodPWM']
                if wvType not in {'rise', 'fall', 'const'}:
                    wvStart = wellinfo['start']

                dp_x = []
                dp_y = []

                if wvType == 'const':
                    dp_x = [programmLen, programmLen + stepLength - self.framerate]
                    dp_y = [wvMax, wvMax]

                # Sine
                elif wvType == 'sin':
                    a = (wvMax - wvMin) / 2
                    b = 2 * np.pi / wvLen
                    d = a + wvMin
                    if wvStart == 'Low':
                        c = - (wvLen/4)
                    elif wvStart == 'High':
                        c = (wvLen/4)

                    time = np.arange(programmLen, programmLen + stepLength, self.framerate)    
                    wave = a * np.sin(b * (time + c)) + d

                    for i in range(len(time)):
                        if i == 0:
                            dp_x.append(time[i])
                            dp_y.append(wave[i])
                        elif i+1 == len(time):
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])
                        else:
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])

                                dp_x.append(time[i])
                                dp_y.append(wave[i])

                # Tri
                elif wvType == 'tri':
                    a = (wvMax - wvMin) / 2
                    d = a + wvMin
                    if wvStart == 'Low':
                        c = - (wvLen/4)
                    elif wvStart == 'High':
                        c = (wvLen/4)

                    time = np.arange(programmLen, programmLen + stepLength, self.framerate)    
                    wave = (4 * a/wvLen * abs(((time + c - wvLen/4) % wvLen) - wvLen/2) - a) + d

                    for i in range(len(time)):
                        if i == 0:
                            dp_x.append(time[i])
                            dp_y.append(wave[i])
                        elif i+1 == len(time):
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])
                        else:
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])

                                dp_x.append(time[i])
                                dp_y.append(wave[i])

                # Square / PWM
                elif wvType in {'pwm', 'sq'}:
                    TimePeriod = periodPWM
                    percent = dutyCyclePWM

                    if wvType == 'sq':
                        TimePeriod = wvLen
                        percent = 0.5

                    time = np.arange(programmLen, programmLen + stepLength, self.framerate)
                    wave = []

                    if wvStart == 'Low':
                        pwm = time % TimePeriod < TimePeriod * percent
                        for dp in pwm:
                            if dp:
                                wave.append(0)
                            else:
                                wave.append(wvMax)
                    elif wvStart == 'High':
                        pwm = time % TimePeriod < TimePeriod * percent
                        for dp in pwm:
                            if dp:
                                wave.append(wvMax)
                            else:
                                wave.append(0)

                    for i in range(len(time)):
                        if i == 0:
                            dp_x.append(time[i])
                            dp_y.append(wave[i])
                        elif i+1 == len(time):
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])
                        else:
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])

                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                
                # Rise
                elif wvType == 'rise':
                    time = np.arange(programmLen, programmLen + stepLength, self.framerate)
                    wave = []

                    diff = wvMax - wvMin
                    dp = wvMin

                    for i in range(len(time)):
                        wave.append(dp)
                        dp += diff/(len(time)-2)

                    for i in range(len(time)):
                        if i == 0:
                            dp_x.append(time[i])
                            dp_y.append(wave[i])
                        elif i+1 == len(time):
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])
                        else:
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])

                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                
                # Fall
                elif wvType == 'fall':
                    time = np.arange(programmLen, programmLen + stepLength, self.framerate)
                    wave = []

                    diff = wvMax - wvMin
                    dp = wvMax

                    for i in range(len(time)):
                        wave.append(dp)
                        dp -= diff/(len(time)-2)

                    for i in range(len(time)):
                        if i == 0:
                            dp_x.append(time[i])
                            dp_y.append(wave[i])
                        elif i+1 == len(time):
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])
                        else:
                            if wave[i] == wave[i-1]:
                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                            else:
                                dp_x.append(time[i])
                                dp_y.append(wave[i-1])

                                dp_x.append(time[i])
                                dp_y.append(wave[i])
                
                if not firstStep:
                     dp_x.insert(0, lastPoint[0])
                     dp_y.insert(0, lastPoint[1])
                else:
                    firstStep = False

                self.pen = pg.mkPen(color=wellinfo['color'], width=2)
                self.graphWidget.plot(dp_x, dp_y, pen=self.pen)

                lastPoint = (dp_x[-1], dp_y[-1])
                programmLen += stepLength - self.framerate

        self.graphWidget.setLimits(xMin = 0, xMax = programmLen, yMin = -1, yMax = 256, minXRange = 5, minYRange = 25)
        self.graphWidget.setXRange(0, programmLen + 3)
        self.graphWidget.setYRange(0, 260)

    def closeEvent(self, event):
        self.closed.emit()