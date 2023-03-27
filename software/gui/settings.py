from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

import numpy as np
import imutils
import os

basedir = os.path.dirname(__file__)

class settingsWindow(QWidget):
    saveSettings = pyqtSignal()
    cancelSettings = pyqtSignal()
    importShape = pyqtSignal()
    exportShape = pyqtSignal()


    def __init__(self, MatSize, framerate, imageType, TL = None, plateNrType = None, customPattern = None):
        super().__init__()
        self.setWindowTitle('Advanced settings')

        self.framerate = framerate
        self.LEDmatrixSize = MatSize
        self.imageType = imageType

        self.plateWidth = 23
        self.plateHeigth = 35
        self.LEDposWellPlate = {0: [], 1: []}
        self.brushSize = 3
        self.brushType = 0
        self.brushShape = 0

        if self.imageType == 'wellplate':
            self.TopLeftLED = TL.copy()
            self.plate_nr_type = plateNrType.copy()
            self.previewArr = np.zeros((self.LEDmatrixSize[0], self.LEDmatrixSize[1]), 'uint8')
        elif self.imageType == 'custompattern':
            self.TopLeftLED = TL.copy()
            self.plate_nr_type = {0: 96, 1: 96}
            self.previewArr = customPattern

        self.mainLayout = QVBoxLayout()

        self._createSettingsForm()
        self._createPreview()
        self._createWellPlateToolbox()
        self._createCustomPatternToolbox()

        if self.imageType == 'wellplate':
            self.createWellPlatePreview(0)
            self.createWellPlatePreview(1)
            self.setPlateMoveRange()
        elif self.imageType == 'custompattern':
            self.updatePreview()

        #Healine
        headlineLabel = QLabel('Advanced settings')
        headlineLabel.setAlignment(Qt.AlignLeft)
        headlineLabel.setStyleSheet('font-size: 25pt; font-weight: bold;')

        # Save Button
        saveSettingsButtonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        saveSettingsButtonBox.accepted.connect(self.saveSettings)
        saveSettingsButtonBox.rejected.connect(self.close)

        # ToolBox Stack
        toolboxWellPlate =  self.settingsWellPlateGBox
        toolboxCustomPattern =  self.settingsCustomPatternGBox
        self.toolboxStack =  QStackedWidget()
        self.toolboxStack.addWidget(toolboxWellPlate)
        self.toolboxStack.addWidget(toolboxCustomPattern)
        if self.imageType == 'wellplate':
            self.toolboxStack.setCurrentIndex(0)
            self.previewLabel.mousePressEvent = self.defaultMouseevent
            self.previewLabel.mouseMoveEvent = self.defaultMouseevent
            self.previewLabel.mouseReleaseEvent = self.defaultMouseevent
        elif self.imageType == 'custompattern':
            self.toolboxStack.setCurrentIndex(1)
            self.previewLabel.mousePressEvent = self.drawLED_click
            self.previewLabel.mouseMoveEvent = self.drawLED_move
            self.previewLabel.mouseReleaseEvent = self.drawLED_release

        #Adding to Layout
        previewToolsLayout = QHBoxLayout()
        previewToolsLayout.addWidget(self.previewGBox, alignment = Qt.AlignCenter)
        previewToolsLayout.addWidget(self.toolboxStack, alignment = Qt.AlignCenter)

        self.mainLayout.addWidget(headlineLabel)
        self.mainLayout.addWidget(self.settingsGBox)
        self.mainLayout.addLayout(previewToolsLayout)
        self.mainLayout.addWidget(saveSettingsButtonBox)

        self.setLayout(self.mainLayout)

    def _createSettingsForm(self):
        self.settingsGBox = QGroupBox("Settings")
        formLayout = QFormLayout()

        ''' 

        MATRIX SIZE CHANGER 

        sizeSelector = QHBoxLayout()
        self.matrixHeight = QSpinBox()
        self.matrixHeight.setValue(64)
        self.matrixHeight.valueChanged.connect(self.setMatrixSize)
        self.matrixWidth = QSpinBox()
        self.matrixWidth.setValue(64)
        self.matrixWidth.valueChanged.connect(self.setMatrixSize)
        sizeSelector.addWidget(self.matrixHeight)
        sizeSelector.addWidget(QLabel('x'))
        sizeSelector.addWidget(self.matrixWidth)
        formLayout.addRow(QLabel('Led Matrix Size:'), sizeSelector)

        '''

        '''

        FRAMERATE CHANGER

        fpsSelector = QHBoxLayout()
        self.fpsMinSB = QSpinBox()
        self.fpsMinSB.setSuffix(' min')
        self.fpsSecSB = QSpinBox()
        self.fpsSecSB.setSuffix(' sec')
        self.fpsSecSB.setMaximum(59)

        # framerate = one frame per 'framerate' seconds
        framerate = 60 * self.framerate
        if framerate < 60:
            self.fpsSecSB.setValue(framerate)
        else:
            self.fpsMinSB.setValue(framerate/60)
            self.fpsSecSB.setValue(framerate%60)

        self.fpsMinSB.valueChanged.connect(self.setFramerate)
        self.fpsSecSB.valueChanged.connect(self.setFramerate)

        fpsSelector.addWidget(QLabel('One frame per '))
        fpsSelector.addWidget(self.fpsMinSB)
        fpsSelector.addWidget(self.fpsSecSB)
        formLayout.addRow(QLabel('Framerate:'), fpsSelector)
        
        '''
        
        self.wellPlateRB = QRadioButton('Well plates')
        self.customPatternRB = QRadioButton('Custom pattern')

        if self.imageType == 'wellplate':
            self.wellPlateRB.setChecked(True)
        elif self.imageType == 'custompattern':
            self.customPatternRB.setChecked(True)

        self.wellPlateRB.toggled.connect(lambda: self.changePatternType(0))
        self.customPatternRB.toggled.connect(lambda: self.changePatternType(1))

        formLayout.addRow(QLabel('Choose illumination type:'), self.wellPlateRB)
        formLayout.addRow(QLabel(), self.customPatternRB)

        self.settingsGBox.setLayout(formLayout)

    def changePatternType(self, imgType):
        if imgType == 0:
            self.imageType = 'wellplate'
            self.toolboxStack.setCurrentIndex(0)
            self.createWellPlatePreview(0)
            self.createWellPlatePreview(1)
            self.setPlateMoveRange()
            self.previewLabel.mousePressEvent = self.defaultMouseevent
            self.previewLabel.mouseMoveEvent = self.defaultMouseevent
            self.previewLabel.mouseReleaseEvent = self.defaultMouseevent
        elif imgType == 1:
            self.imageType = 'custompattern'
            self.toolboxStack.setCurrentIndex(1)
            self.previewArr = np.zeros((self.LEDmatrixSize[0], self.LEDmatrixSize[1]), 'uint8')
            self.updatePreview()

            self.previewLabel.mousePressEvent = self.drawLED_click
            self.previewLabel.mouseMoveEvent = self.drawLED_move
            self.previewLabel.mouseReleaseEvent = self.drawLED_release

    # WellPlate 
    def _createWellPlateToolbox(self):
        self.settingsWellPlateGBox = QGroupBox("Well Plate Settings")

        toolboxLayout = QVBoxLayout()
        # Plate 1
        P1_title = QLabel('Plate 1')
        P1_title.setAlignment(Qt.AlignLeft)
        P1_title.setStyleSheet('font-weight: bold')

        P1_positionLayout = QFormLayout()

        P1_TypeCB = QComboBox()
        P1_TypeCB.addItem("96-well Plate")
        #self.P1_TypeCB.addItem("48-well Plate")
        P1_TypeCB.addItem("24-well Plate")
        P1_TypeCB.addItem("6-well Plate")
        P1_TypeCB.currentIndexChanged.connect(lambda ignore: self.changePlateType(0, P1_TypeCB.currentText()))

        P1_positionLayout.addRow(QLabel('Plate 1 Type:'), P1_TypeCB) 

        P1_TL_Layout = QHBoxLayout()
        self.P1_TL_Height = QSpinBox()
        self.P1_TL_Height.setValue(self.TopLeftLED[0][0])
        self.P1_TL_Height.valueChanged.connect(lambda ignore: self.movePlate(0, TL = (self.P1_TL_Height.value(), self.P1_TL_Width.value())))
        self.P1_TL_Width = QSpinBox()
        self.P1_TL_Width.setValue(self.TopLeftLED[0][1])
        self.P1_TL_Width.valueChanged.connect(lambda ignore: self.movePlate(0, TL = (self.P1_TL_Height.value(), self.P1_TL_Width.value())))
        P1_TL_Layout.addWidget(QLabel('h: '))
        P1_TL_Layout.addWidget(self.P1_TL_Height)
        P1_TL_Layout.addWidget(QLabel('w: '))
        P1_TL_Layout.addWidget(self.P1_TL_Width)

        P1_positionLayout.addRow(QLabel('Plate 1 Top-Left LED:'), P1_TL_Layout) 

        # Move Arrows P1
        
        P1_mvUpButton = QPushButton()
        P1_mvUpButton.clicked.connect(lambda ignore: self.movePlate(0, direction = 'up'))
        P1_mvUpButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P1_mvUpButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-up.svg')))
        P1_mvUpButton.setFixedSize(26,26)
        P1_mvDownButton = QPushButton()
        P1_mvDownButton.clicked.connect(lambda ignore: self.movePlate(0, direction = 'down'))
        P1_mvDownButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P1_mvDownButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-down.svg')))
        P1_mvDownButton.setFixedSize(26,26)
        P1_mvLeftButton = QPushButton()
        P1_mvLeftButton.clicked.connect(lambda ignore: self.movePlate(0, direction = 'left'))
        P1_mvLeftButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P1_mvLeftButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-left.svg')))
        P1_mvLeftButton.setFixedSize(26,26)
        P1_mvRightButton = QPushButton()
        P1_mvRightButton.clicked.connect(lambda ignore: self.movePlate(0, direction = 'right'))
        P1_mvRightButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P1_mvRightButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-right.svg')))
        P1_mvRightButton.setFixedSize(26,26)
        P1_resetButton = QPushButton()
        P1_resetButton.clicked.connect(lambda ignore: self.movePlate(0, direction = 'reset'))
        P1_resetButton.setStyleSheet("border: 0px solid black")
        P1_resetButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'settings-reset.svg')))
        P1_resetButton.setFixedSize(26,26)

        P1_MoveLayout = QHBoxLayout()
        P1_arrowLayout = QGridLayout()
        P1_arrowLayout.addWidget(P1_mvUpButton, 0, 1, 1, 1)
        P1_arrowLayout.addWidget(P1_mvDownButton, 2, 1, 1, 1)
        P1_arrowLayout.addWidget(P1_mvLeftButton, 1, 0, 1, 1)
        P1_arrowLayout.addWidget(P1_mvRightButton, 1, 2, 1, 1)
        P1_arrowLayout.addWidget(P1_resetButton, 1, 1, 1, 1)
        P1_MoveLayout.addStretch()
        P1_MoveLayout.addLayout(P1_arrowLayout)
        P1_MoveLayout.addStretch()

        #Plate 2
        P2_title = QLabel('Plate 2')
        P2_title.setAlignment(Qt.AlignLeft)
        P2_title.setStyleSheet('font-weight: bold')

        P2_positionLayout = QFormLayout()

        P2_TypeCB = QComboBox()
        P2_TypeCB.addItem("96-well Plate")
        #self.P2_TypeCB.addItem("48-well Plate")
        P2_TypeCB.addItem("24-well Plate")
        P2_TypeCB.addItem("6-well Plate")
        P2_TypeCB.currentIndexChanged.connect(lambda ignore: self.changePlateType(1, P2_TypeCB.currentText()))

        P2_positionLayout.addRow(QLabel('Plate 2 Type:'), P2_TypeCB) 

        P2_TL_Layout = QHBoxLayout()
        self.P2_TL_Height = QSpinBox()
        self.P2_TL_Height.setValue(self.TopLeftLED[1][0])
        self.P2_TL_Height.valueChanged.connect(lambda ignore: self.movePlate(1, TL = (self.P2_TL_Height.value(), self.P2_TL_Width.value())))
        self.P2_TL_Width = QSpinBox()
        self.P2_TL_Width.setValue(self.TopLeftLED[1][1])
        self.P2_TL_Width.valueChanged.connect(lambda ignore: self.movePlate(1, TL = (self.P2_TL_Height.value(), self.P2_TL_Width.value())))
        P2_TL_Layout.addWidget(QLabel('h: '))
        P2_TL_Layout.addWidget(self.P2_TL_Height)
        P2_TL_Layout.addWidget(QLabel('w: '))
        P2_TL_Layout.addWidget(self.P2_TL_Width)

        P2_positionLayout.addRow(QLabel('Plate 2 Top-Left LED:'), P2_TL_Layout) 

        # Move Arrows P2
        
        P2_mvUpButton = QPushButton()
        P2_mvUpButton.clicked.connect(lambda ignore: self.movePlate(1, direction = 'up'))
        P2_mvUpButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P2_mvUpButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-up.svg')))
        P2_mvUpButton.setFixedSize(26,26)
        P2_mvDownButton = QPushButton()
        P2_mvDownButton.clicked.connect(lambda ignore: self.movePlate(1, direction = 'down'))
        P2_mvDownButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P2_mvDownButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-down.svg')))
        P2_mvDownButton.setFixedSize(26,26)
        P2_mvLeftButton = QPushButton()
        P2_mvLeftButton.clicked.connect(lambda ignore: self.movePlate(1, direction = 'left'))
        P2_mvLeftButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P2_mvLeftButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-left.svg')))
        P2_mvLeftButton.setFixedSize(26,26)
        P2_mvRightButton = QPushButton()
        P2_mvRightButton.clicked.connect(lambda ignore: self.movePlate(1, direction = 'right'))
        P2_mvRightButton.setStyleSheet("border-radius : 13; border: 1px solid black;")
        P2_mvRightButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-right.svg')))
        P2_mvRightButton.setFixedSize(26,26)
        P2_resetButton = QPushButton()
        P2_resetButton.clicked.connect(lambda ignore: self.movePlate(1, direction = 'reset'))
        P2_resetButton.setStyleSheet("border: 0px solid black")
        P2_resetButton.setIcon(QIcon(os.path.join(basedir, 'resources', 'settings-reset.svg')))
        P2_resetButton.setFixedSize(26,26)

        P2_MoveLayout = QHBoxLayout()
        P2_arrowLayout = QGridLayout()
        P2_arrowLayout.addWidget(P2_mvUpButton, 0, 1, 1, 1)
        P2_arrowLayout.addWidget(P2_mvDownButton, 2, 1, 1, 1)
        P2_arrowLayout.addWidget(P2_mvLeftButton, 1, 0, 1, 1)
        P2_arrowLayout.addWidget(P2_mvRightButton, 1, 2, 1, 1)
        P2_arrowLayout.addWidget(P2_resetButton, 1, 1, 1, 1)
        P2_MoveLayout.addStretch()
        P2_MoveLayout.addLayout(P2_arrowLayout)
        P2_MoveLayout.addStretch()

        toolboxLayout.addWidget(P1_title)
        toolboxLayout.addLayout(P1_positionLayout)
        toolboxLayout.addLayout(P1_MoveLayout)
        toolboxLayout.addItem(QSpacerItem(20, 20))
        toolboxLayout.addWidget(P2_title)
        toolboxLayout.addLayout(P2_positionLayout)
        toolboxLayout.addLayout(P2_MoveLayout)

        self.settingsWellPlateGBox.setLayout(toolboxLayout)
    
    def createWellPlatePreview(self, plateNr):

        for LED in self.LEDposWellPlate[plateNr]:
            self.previewArr[LED[1], LED[0]] = 0 

        TL = self.TopLeftLED[plateNr]
        self.LEDposWellPlate[plateNr] = []

        if self.plate_nr_type[plateNr] == 96:
            for row in range(12):
                for col in range(8):
                    led_pos_y = [row*3 + TL[0], row*3 + TL[0] + 1]
                    led_pos_x = [col*3 + TL[1], col*3 + TL[1] + 1]
                    for x in range(2):
                        for y in range(2):
                            led = (led_pos_x[x], led_pos_y[y])
                            self.LEDposWellPlate[plateNr].append(led)

        if self.plate_nr_type[plateNr] == 24:
            for row in range(6):
                for col in range(4):
                    led_pos_x = []
                    led_pos_y = []
                    for i in range(5):
                        led_pos_temp = row*6+TL[0]+i
                        led_pos_y.append(led_pos_temp)
                    for i in range(5):
                        led_pos_temp = col*6+TL[1]+i
                        led_pos_x.append(led_pos_temp)

                    for x in range(5):
                        if x == 0 or x == 4:
                            for y in range(3):
                                led = (led_pos_x[x], led_pos_y[y+1])
                                self.LEDposWellPlate[plateNr].append(led)
                        else:
                            for y in range(5):
                                led = (led_pos_x[x], led_pos_y[y]) 
                                self.LEDposWellPlate[plateNr].append(led)

        if self.plate_nr_type[plateNr] == 6:
            ledPerRow = 5
            for row in range(3):
                for col in range(2):
                    led_pos_x = []
                    led_pos_y = []
                    for i in range(11):
                        led_pos_temp = row*12+TL[0]+i
                        led_pos_y.append(led_pos_temp)
                    for i in range(11):
                        led_pos_temp = col*12+TL[1]+i
                        led_pos_x.append(led_pos_temp)

                    for x in range(11):
                        if x == 0 or x == 10:
                            for y in range(5):
                                led = (led_pos_x[x], led_pos_y[y+3])
                                self.LEDposWellPlate[plateNr].append(led)
                        elif x == 1 or x == 9:
                            for y in range(7):
                                led = (led_pos_x[x], led_pos_y[y+2])
                                self.LEDposWellPlate[plateNr].append(led)
                        elif x == 2 or x == 8:
                            for y in range(9):
                                led = (led_pos_x[x], led_pos_y[y+1])
                                self.LEDposWellPlate[plateNr].append(led)
                        else:
                            for y in range(11):
                                led = (led_pos_x[x], led_pos_y[y]) 
                                self.LEDposWellPlate[plateNr].append(led)

        for LED in self.LEDposWellPlate[plateNr]:
            self.previewArr[LED[1], LED[0]] = 255

        self.updatePreview()

    def changePlateType(self, plateNr, plateType):
        if plateType == '96-well Plate':
            self.plate_nr_type[plateNr] = 96
        elif plateType == '24-well Plate':
            self.plate_nr_type[plateNr] = 24
        elif plateType == '6-well Plate':
            self.plate_nr_type[plateNr] = 6

        self.createWellPlatePreview(plateNr)

    def movePlate(self, plateNr, TL = None, direction = None):
        if TL is None:
            self.P1_TL_Width.blockSignals(True)
            self.P1_TL_Height.blockSignals(True)
            self.P2_TL_Width.blockSignals(True)
            self.P2_TL_Height.blockSignals(True)
            if direction == 'up':
                newTL = (self.TopLeftLED[plateNr][0] - 1, self.TopLeftLED[plateNr][1])
                if plateNr == 0:
                    self.P1_TL_Width.setValue(newTL[1])
                    self.P1_TL_Height.setValue(newTL[0])
                else:
                    self.P2_TL_Width.setValue(newTL[1])
                    self.P2_TL_Height.setValue(newTL[0])
            elif direction == 'down':
                newTL = (self.TopLeftLED[plateNr][0] + 1, self.TopLeftLED[plateNr][1])
                if plateNr == 0:
                    self.P1_TL_Width.setValue(newTL[1])
                    self.P1_TL_Height.setValue(newTL[0])
                else:
                    self.P2_TL_Width.setValue(newTL[1])
                    self.P2_TL_Height.setValue(newTL[0])
            elif direction == 'left':
                newTL = (self.TopLeftLED[plateNr][0], self.TopLeftLED[plateNr][1] - 1)
                if plateNr == 0:
                    self.P1_TL_Width.setValue(newTL[1])
                    self.P1_TL_Height.setValue(newTL[0])
                else:
                    self.P2_TL_Width.setValue(newTL[1])
                    self.P2_TL_Height.setValue(newTL[0])
            elif direction == 'right':
                newTL = (self.TopLeftLED[plateNr][0], self.TopLeftLED[plateNr][1] + 1)
                if plateNr == 0:
                    self.P1_TL_Width.setValue(newTL[1])
                    self.P1_TL_Height.setValue(newTL[0])
                else:
                    self.P2_TL_Width.setValue(newTL[1])
                    self.P2_TL_Height.setValue(newTL[0])
            elif direction == 'reset':
                if plateNr == 0:
                    newTL = (15, 4)
                    self.P1_TL_Width.setValue(newTL[1])
                    self.P1_TL_Height.setValue(newTL[0])
                elif plateNr == 1:
                    newTL = (15, 37)
                    self.P2_TL_Width.setValue(newTL[1])
                    self.P2_TL_Height.setValue(newTL[0])
            self.P1_TL_Width.blockSignals(False)
            self.P1_TL_Height.blockSignals(False)
            self.P2_TL_Width.blockSignals(False)
            self.P2_TL_Height.blockSignals(False)

            if plateNr == 0:
                if newTL[0] <= (self.minTL_H  - 1) or newTL[0] >= (self.maxTL_H + 1) or\
                 newTL[1] <= (self.P1_minTL_W  - 1) or newTL[1] >= (self.P1_maxTL_W + 1):
                    return
            elif plateNr == 1:
                if newTL[0] <= (self.minTL_H  - 1) or newTL[0] >= (self.maxTL_H + 1) or\
                 newTL[1] <= (self.P2_minTL_W  - 1) or newTL[1] >= (self.P2_maxTL_W + 1):
                    return
        
        elif direction is None:
            newTL = TL
        
        self.TopLeftLED[plateNr] = newTL
        self.createWellPlatePreview(plateNr)
        self.setPlateMoveRange()

    def setPlateMoveRange(self):
        self.P1_TL_Width.blockSignals(True)
        self.P1_TL_Height.blockSignals(True)
        self.P2_TL_Width.blockSignals(True)
        self.P2_TL_Height.blockSignals(True)

        self.minTL_H = 0
        self.maxTL_H = self.LEDmatrixSize[0] - self.plateHeigth

        self.P1_minTL_W = 0
        self.P1_maxTL_W = self.TopLeftLED[1][1] - self.plateWidth - 2
        self.P2_minTL_W = self.TopLeftLED[0][1] + self.plateWidth + 2
        self.P2_maxTL_W = self.LEDmatrixSize[1] - self.plateWidth
        
        self.P1_TL_Width.setMaximum(self.TopLeftLED[1][1] - self.plateWidth - 2)
        self.P1_TL_Height.setMaximum(self.LEDmatrixSize[0] - self.plateHeigth)

        self.P2_TL_Width.setMinimum(self.TopLeftLED[0][1] + self.plateWidth + 2)
        self.P2_TL_Width.setMaximum(self.LEDmatrixSize[1] - self.plateWidth)
        self.P2_TL_Height.setMaximum(self.LEDmatrixSize[0] - self.plateHeigth)

        self.P1_TL_Width.blockSignals(False)
        self.P1_TL_Height.blockSignals(False)
        self.P2_TL_Width.blockSignals(False)
        self.P2_TL_Height.blockSignals(False)

    def defaultMouseevent(self, event):
        pass

    # Custom Shape
    def _createCustomPatternToolbox(self):
        self.settingsCustomPatternGBox = QGroupBox("Custom Shape Settings")

        toolboxLayout = QVBoxLayout()
        # Gereral
        gereralTitle = QLabel('General')
        gereralTitle.setAlignment(Qt.AlignLeft)
        gereralTitle.setStyleSheet('font-weight: bold')

        selectAllButton = QPushButton('Select all')
        selectAllButton.clicked.connect(self.selectAll)
        deselectAllButton = QPushButton('Clear all')
        deselectAllButton.clicked.connect(self.clearAll)
        invertButton = QPushButton('Invert')
        invertButton.clicked.connect(self.invert)

        generalLayout = QHBoxLayout()
        generalLayout.addWidget(selectAllButton)
        generalLayout.addWidget(deselectAllButton)
        generalLayout.addWidget(invertButton)

        # Brush settings
        brushTitle = QLabel('Brush settings')
        brushTitle.setAlignment(Qt.AlignLeft)
        brushTitle.setStyleSheet('font-weight: bold')

        # Type Settings
        typeBG = QButtonGroup(self.settingsCustomPatternGBox)
        brushTypeDrawRB = QRadioButton('Draw')
        brushTypeDrawRB.setChecked(True)
        brushTypeDrawRB.toggled.connect(lambda: self.updateBrush(brushType = 0))
        brushTypeEraseRB = QRadioButton('Erase')
        brushTypeEraseRB.toggled.connect(lambda: self.updateBrush(brushType = 1))
        typeBG.addButton(brushTypeDrawRB)
        typeBG.addButton(brushTypeEraseRB)        

        # Shape Settings
        shapeBG = QButtonGroup(self.settingsCustomPatternGBox)
        brushShapeSquareRB = QRadioButton('Square brush')
        brushShapeSquareRB.setChecked(True)
        brushShapeSquareRB.toggled.connect(lambda: self.updateBrush(shape = 0))
        brushShapeRoundRB = QRadioButton('Round brush')
        brushShapeRoundRB.toggled.connect(lambda: self.updateBrush(shape = 1))
        shapeBG.addButton(brushShapeSquareRB)
        shapeBG.addButton(brushShapeRoundRB) 

        # SIZE SETTINGS
        brushSizeSB = QSpinBox()
        brushSizeSB.setMaximum(15)
        brushSizeSB.setMinimum(1)
        brushSizeSB.setValue(self.brushSize)
        brushSizeSlider = QSlider(Qt.Horizontal)
        brushSizeSlider.setMaximum(15)
        brushSizeSlider.setMinimum(1)
        brushSizeSlider.setValue(self.brushSize)

        brushSizeSB.valueChanged.connect(lambda ignore: brushSizeSlider.setValue(brushSizeSB.value()))
        brushSizeSB.valueChanged.connect(lambda: self.updateBrush(size = brushSizeSB.value()))
        brushSizeSlider.valueChanged.connect(lambda ignore: brushSizeSB.setValue(brushSizeSlider.value()))
        brushSizeSlider.valueChanged.connect(lambda: self.updateBrush(size = brushSizeSlider.value()))

        sizeLayout = QHBoxLayout()
        sizeLayout.addWidget(brushSizeSB)
        sizeLayout.addWidget(brushSizeSlider)

        # Brush Layout
        brushLayout = QFormLayout()
        brushLayout.addRow(QLabel('Brush type:'), brushTypeDrawRB)
        brushLayout.addRow(QLabel(), brushTypeEraseRB)
        brushLayout.addRow(QLabel('Brush shape:'), brushShapeSquareRB)
        brushLayout.addRow(QLabel(), brushShapeRoundRB)
        brushLayout.addRow(QLabel('Brush size:'), sizeLayout)

        # Import/Export
        im_exportTitle = QLabel('Import / Export shape')
        im_exportTitle.setAlignment(Qt.AlignLeft)
        im_exportTitle.setStyleSheet('font-weight: bold')

        importButton = QPushButton('Import')
        importButton.clicked.connect(self.importShape)
        exportButton = QPushButton('Export')
        exportButton.clicked.connect(self.exportShape)

        im_exportLayout = QHBoxLayout()
        im_exportLayout.addWidget(importButton)
        im_exportLayout.addWidget(exportButton)

        toolboxLayout.addWidget(gereralTitle)
        toolboxLayout.addLayout(generalLayout)
        toolboxLayout.addWidget(brushTitle)
        toolboxLayout.addLayout(brushLayout)
        toolboxLayout.addWidget(im_exportTitle)
        toolboxLayout.addLayout(im_exportLayout)
        toolboxLayout.addStretch()

        self.settingsCustomPatternGBox.setLayout(toolboxLayout)

    def selectAll(self):
        self.previewArr[:, :] = 255 
        self.updatePreview()

    def clearAll(self):
        self.previewArr[:, :] = 0 
        self.updatePreview()

    def invert(self):
        for y in range(self.previewArr.shape[0]):
            for x in range(self.previewArr.shape[1]):
                if self.previewArr[y][x] != 0:
                    self.previewArr[y][x] = 0
                else:
                    self.previewArr[y][x] = 255

        self.updatePreview()

    def updateBrush(self, brushType = None, shape = None, size = None):
        if size is not None:
            self.brushSize = size
        if shape is not None:
            # Shape: 0 = SQUARE; 1 = CIRCLE
            self.brushShape = shape
        if brushType is not None:
            # Type: 0 = DRAW; 1 = ERASE
            self.brushType = brushType

    def modifyPattern(self, pos):
        if self.brushType == 0:
            value = 255
        elif self.brushType == 1:
            value = 0

        gridPos = (round(pos[0]/self.sc), round(pos[1]/self.sc))
        ledPos = (round((gridPos[0] - 1) / 2), round((gridPos[1] - 1) / 2))

        if self.brushShape == 0:
            brushTL = (ledPos[0] - int((self.brushSize - 1)/2), ledPos[1] - int((self.brushSize - 1)/2))
            self.previewArr[brushTL[1]:(brushTL[1]+self.brushSize),  brushTL[0]:(brushTL[0]+self.brushSize)] = value
        elif self.brushShape == 1:
            x = np.arange(0, self.LEDmatrixSize[0])
            y = np.arange(0, self.LEDmatrixSize[1])
            r = self.brushSize/2
            mask = (x[np.newaxis,:]-ledPos[0])**2 + (y[:,np.newaxis]-ledPos[1])**2 < r**2
            self.previewArr[mask] = value

        self.updatePreview()

    def drawLED_click(self , event):
        self.modifyPattern((event.x(), event.y()))
        self.drawing = True
    def drawLED_move(self , event):
        if self.drawing:
            self.modifyPattern((event.x(), event.y()))
    def drawLED_release(self, event):

        self.drawing = False


    # Preview
    def _createPreview(self):
        self.previewGBox = QGroupBox("Preview")
        previewLayout = QVBoxLayout()

        # Pixmap Preview
        self.previewLabel = QLabel()
        self.previewLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.previewLabel.setAlignment(Qt.AlignCenter)
        previewLayout.addWidget(self.previewLabel)

        self.previewGBox.setLayout(previewLayout)   

    def updatePreview(self):
        LED_OFF_RGB = (20, 20, 20)
        LED_ON_RGB = (0, 255, 255)
        GRID_RGB = (100, 100, 100)

        PREVIEW_WIDTH = 450

        gridArr = np.zeros((self.LEDmatrixSize[0] * 2 - 1, self.LEDmatrixSize[1] * 2 - 1, 3), 'uint8')
        for y in range(gridArr.shape[0]):
            for x in range(gridArr.shape[1]):
                for i, rgb in enumerate(LED_OFF_RGB):
                    gridArr[y][x][i] = rgb

        for y in range(gridArr.shape[0]):
            if y%2 != 0:
                for x in range(gridArr.shape[1]):
                    for i, rgb in enumerate(GRID_RGB):
                        gridArr[y][x][i] = rgb

            else:
                for x in range(gridArr.shape[1]):
                    if x%2 != 0:
                        for i, rgb in enumerate(GRID_RGB):
                            gridArr[y][x][i] = rgb

        for y in range(self.previewArr.shape[0]):
            for x in range(self.previewArr.shape[1]):
                if self.previewArr[y][x] != 0:
                    for i, rgb in enumerate(LED_ON_RGB):
                        gridArr[2*y][2*x][i] = rgb

        image = gridArr
        image = imutils.resize(image,width=PREVIEW_WIDTH)
        self.sc = PREVIEW_WIDTH/gridArr.shape[0]
        frame = image
        image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        self.previewLabel.setPixmap(QPixmap.fromImage(image))

    def importData(self, imgType, TL = None, customPattern = None):
        if imgType != self.imageType:
            if imgType == 'wellplate':
                self.wellPlateRB.setChecked(True)
                self.customPatternRB.setChecked(False)
                self.changePatternType(0)
            elif imgType == 'custompattern':
                self.wellPlateRB.setChecked(False)
                self.customPatternRB.setChecked(True)
                self.changePatternType(1)

        if self.imageType == 'wellplate':
            self.TopLeftLED = TL.copy()
            self.previewArr = np.zeros((self.LEDmatrixSize[0], self.LEDmatrixSize[1]), 'uint8')
            self.movePlate(0, TL[0])
            self.movePlate(1, TL[1])
        elif self.imageType == 'custompattern':
            self.clearAll()
            self.previewArr = customPattern
            self.updatePreview()



    def closeEvent(self, event):
        self.cancelSettings.emit()



''' 
    def setFramerate(self):
        self.framerate = self.fpsSecSB.value() / 60 + self.fpsMinSB.value()
'''
'''
    def setMatrixSize(self):
        self.LEDmatrixSize = (self.matrixHeight.value(), self.matrixWidth.value())
        self.previewArr = np.zeros((self.LEDmatrixSize[0], self.LEDmatrixSize[1]), 'uint8')
        self.createWellPlatePreview(0)
        self.createWellPlatePreview(1)
        self.setPlateMoveRange()
'''