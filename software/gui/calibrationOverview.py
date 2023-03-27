from PyQt5.QtWidgets import * 
from PyQt5.QtCore import * 

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)  
   
#Main Window
class calibrationOverview(QWidget):
    _calibrate = pyqtSignal(str)
    _reset = pyqtSignal()
    def __init__(self):
        super().__init__()
   
        self.overviewLay = QGridLayout() 

        titleColor = QLabel('LED Color')
        titleColor.setStyleSheet("font-weight: bold;")
        titleType = QLabel('Plate Type')
        titleType.setStyleSheet("font-weight: bold;")
        titleNr = QLabel('Plate Nr')
        titleNr.setStyleSheet("font-weight: bold;")
        titleDone = QLabel('Calibrated')
        titleDone.setStyleSheet("font-weight: bold;")
        
        self.overviewLay.addWidget(titleColor, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        self.overviewLay.addWidget(titleType, 0, 1, 1, 1, alignment=Qt.AlignCenter)
        self.overviewLay.addWidget(titleNr, 0, 2, 1, 1, alignment=Qt.AlignCenter)
        self.overviewLay.addWidget(titleDone, 0, 3, 1, 1, alignment=Qt.AlignCenter)
        self.overviewLay.addItem(QSpacerItem(110, 0, QSizePolicy.Minimum, QSizePolicy.Minimum), 0, 4, 1, 1)

        self._createScrollWidgets()
        self._createScrollOverview()

        self.overviewLay.addWidget(self.scrollOverview, 1, 0, 20, 5)

    def _createScrollOverview(self):
        self.scrollOverview = QScrollArea()
        self.scrollWidget = QWidget()
        self.scrollVBox = QVBoxLayout()

        #self.scrollVBox.addWidget(QHLine())
        for cn in self.scrollLays.keys():
            self.scrollVBox.addLayout(self.scrollLays[cn])
            self.scrollVBox.addWidget(QHLine())

        resetLay = QHBoxLayout()
        resetLay.addStretch()
        resetLay.addWidget(self.resetButton)
        self.scrollVBox.addLayout(resetLay)
        
        self.scrollWidget.setLayout(self.scrollVBox)

        self.scrollOverview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollOverview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollOverview.setWidgetResizable(True)
        self.scrollOverview.setWidget(self.scrollWidget)

    def _createScrollWidgets(self):
        self.caliButtons = {}
        self.caliLabels = {}
        self.scrollLays = {}

        colors = ['Red', 'Green', 'Blue']
        platetypes = [96, 24, 6]
        plateNrs = [1, 2]

        self.caliNames = []
        for color in ['R', 'G', 'B']:
            for plateType in ['96', '24', '6']:
                for plateNr in ['1', '2']:
                    self.caliNames.append(str(color + '-' + plateType + '-' + plateNr))

        for caliName in self.caliNames:
            self.scrollLays[caliName] = QHBoxLayout()

        cn = 0
        for i, color in enumerate(colors):
            i = i*6
            for j in range(6):
                self.scrollLays[self.caliNames[cn]].addWidget(QLabel(color), alignment=Qt.AlignCenter)
                cn += 1

        cn = 0
        for i in range(0, 18, 6):
            for j, platetype in enumerate(platetypes):
                j = j*2
                for k in range(2):
                    self.scrollLays[self.caliNames[cn]].addWidget(QLabel(str(platetype)), alignment=Qt.AlignCenter)
                    cn += 1
        
        cn = 0
        for i in range(0, 18, 2):
            for j, plateNr in enumerate(plateNrs):
                self.scrollLays[self.caliNames[cn]].addWidget(QLabel(str(plateNr)), alignment=Qt.AlignCenter)
                cn += 1
        
        cn = 0
        for i in range(0, 18):
            caliID = self.caliNames[i]
            self.caliLabels[caliID] = QLabel('No', self)
            self.caliLabels[caliID].setStyleSheet("background-color: rgb(255, 204, 203);")
            self.scrollLays[self.caliNames[cn]].addWidget(self.caliLabels[caliID], alignment=Qt.AlignCenter)
            cn += 1

        cn = 0
        for i in range(0, 18):
            caliID = self.caliNames[i]
            self.caliButtons[caliID] = QPushButton('Calibrate', self)
            self.caliButtons[caliID].clicked.connect(lambda ignore, i=caliID: self._calibrate.emit(i))
            self.scrollLays[self.caliNames[cn]].addWidget(self.caliButtons[caliID], alignment=Qt.AlignCenter)
            cn += 1

        self.resetButton = QPushButton('Reset all', self)
        self.resetButton.clicked.connect(self._reset)


    def setCalibrated(self, caliID, calibrated):
        if calibrated:
            self.caliLabels[caliID].setText('Yes')
            self.caliLabels[caliID].setStyleSheet("background-color: rgb(144, 248, 144);")
        else:
            self.caliLabels[caliID].setText('No')
            self.caliLabels[caliID].setStyleSheet("background-color: rgb(255, 204, 203);")

    def calibrationProgress(self, caliID = None, calibrated = False):
        for key in self.caliButtons.keys():
            self.caliButtons[key].setText('Calibrate')
        if not calibrated:
            self.caliButtons[caliID].setText('In progress')

