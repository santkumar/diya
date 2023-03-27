from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

from PIL import Image
import numpy as np

import cv2, imutils, tifffile
import os

from calibrationOverview import *


basedir = os.path.dirname(__file__)

def sort_contours(cnts, method="left-to-right"):
    reverse = False
    i = 0

    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1

    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda ax: (ax[1][0], ax[1][1])))

    return cnts

def draw_contour(image, c, i):
    
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    cv2.putText(image, "#{}".format(i + 1), (cX - 15, cY + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return image

def read_image_uint8(path):
    if path.endswith('.tiff') or path.endswith('.tif'):
        data = tifffile.imread(path)
    else:
        img = Image.open(path)
        data = np.asarray(img)

    if len(data.shape) == 3:
        data = np.dot(data[...,:3], [0.2989, 0.5870, 0.1140])

    data = imutils.resize(data,height=500)

    if data.dtype != np.uint8:
        img_8bit = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        return img_8bit

    elif data.dtype == np.uint8:
        return data

    else:
        raise TypeError('Datatype not supported') 

def calibrate(c, img):
    M = cv2.moments(c)
    c2d = c[:,0,:]

    wellMinY = np.min(c2d[:,1])
    wellMidX = int(M["m10"] / M["m00"])
    wellMidY = int(M["m01"] / M["m00"])
    wellMid = (wellMidX, wellMidY)
    wellradius = int((wellMidY - wellMinY) * 0.7)

    mask = np.zeros((img.shape[0], img.shape[1]))
    mask = cv2.circle(mask, wellMid, wellradius, 1, cv2.FILLED)
    mask = mask.astype('bool')
    idxs = np.transpose((mask > 0).nonzero())

    intensitys = []

    for idx in idxs:
        val = img[idx[0], idx[1]]
        intensitys.append(val)
    
    intensitys = np.array(intensitys)
    wellMean = np.mean(intensitys)
    
    return wellradius, wellMid, wellMean
    

class calibrationWindow(QWidget):
    getCaliData = pyqtSignal()
    cancelCali = pyqtSignal()
    def __init__(self, caliKi):
        super().__init__()

        # Set Variables
        self.setWindowTitle('Calibration')

        self.filename = None # Will hold the image address location
        self.tmp = None # Will hold the temporary image for display

        self.exportPath = None
        self.export = False

        self.caliKi = caliKi
        self.caliID = None

        # Setup
        self.mainLayout = QHBoxLayout()

        self.wellAmount = None
        self.blurrValue = 5

        self.mainLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()

        #Healine
        headlineLabel = QLabel('Calibration')
        headlineLabel.setAlignment(Qt.AlignLeft)
        headlineLabel.setStyleSheet('font-size: 25pt; font-weight: bold;')

        self._createPreview()
        self._createOverview()

        self.setParaDisabled(True)

        self.topLayout.addWidget(self.analyseGB)   
        self.topLayout.insertWidget(0, self.overviewGB)

        self.mainLayout.addWidget(headlineLabel)
        self.mainLayout.addLayout(self.topLayout)

        self.finishButtonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        self.finishButtonBox.accepted.connect(self.getCaliData)
        self.finishButtonBox.rejected.connect(self.cancelCali)
        self.mainLayout.addWidget(self.finishButtonBox)

        self.setLayout(self.mainLayout)
        
    
    def _createPreview(self):
        self.analyseGB = QGroupBox()

        self.TitleLabel = QLabel()
        self.TitleLabel.setText("Upload Calibration Image")
        self.TitleLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setStyleSheet("font-weight: bold")

        self.previewLabel = QLabel()
        self.previewLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.previewLabel.setAlignment(Qt.AlignCenter)
        tmp = read_image_uint8(os.path.join(basedir, 'resources', '96-well-template.png'))
        self.setPhoto(tmp)

        self.blurrSlider = QSlider(Qt.Horizontal)
        self.blurrSlider.setMaximum(29)
        self.blurrSlider.setValue(5)
        self.blurrSlider.valueChanged.connect(self.setBlurrValue)
                
        self.blurrButton = QPushButton('Show blurred image')
        self.blurrButton.clicked.connect(self.showBlurrImage)

        self.blurrLabel = QLabel('Set blurr intensity\n(only for well detection)')

        self.detectButton = QPushButton('Detect wells')
        self.detectButton.clicked.connect(self.detectWells)

        self.showButton = QPushButton('Show original image')
        self.showButton.clicked.connect(self.showPhoto)

        self.caliButton = QPushButton('Calibrate plate')
        self.caliButton.clicked.connect(self.calibratePlate)

        prevLay = QVBoxLayout()
        prevLay.addWidget(self.TitleLabel)
        prevLay.addWidget(self.previewLabel)

        paraLay = QVBoxLayout()
        paraLay.addStretch()
        paraLay.addWidget(self.blurrLabel)
        paraLay.addWidget(self.blurrSlider)
        paraLay.addWidget(QHLine())
        paraLay.addWidget(self.blurrButton)
        paraLay.addWidget(self.showButton)
        paraLay.addWidget(QHLine())
        paraLay.addWidget(self.detectButton)
        paraLay.addWidget(self.caliButton)

        analyseLay = QHBoxLayout()
        analyseLay.addLayout(prevLay)
        analyseLay.addLayout(paraLay)

        self.analyseGB.setLayout(analyseLay)

    def _createOverview(self):
        self.overview = calibrationOverview()
        self.overview._calibrate.connect(self.loadImage)
        self.overview._reset.connect(self.resetAll)

        for caliID, Kis in self.caliKi.items():
            if Kis is not None:
                self.overview.setCalibrated(caliID, True)

        self.overviewGB = QGroupBox('Overview')
        self.overviewGB.setLayout(self.overview.overviewLay)

    def setParaDisabled(self, disabled):
        self.blurrLabel.setDisabled(disabled)
        self.blurrSlider.setDisabled(disabled)
        self.blurrButton.setDisabled(disabled)
        self.detectButton.setDisabled(disabled)
        self.showButton.setDisabled(disabled)
        self.caliButton.setDisabled(disabled)
        
    def loadImage(self, caliID):
        self.caliID = caliID
        self.platetype = int(self.caliID.rstrip('12').strip('RGB-'))

        self.filename = QFileDialog.getOpenFileName(self,
            self.tr("Open calibration image"), "",
            self.tr("Images (*.tif *.tiff *.jpg *.JPG *.png)"))[0]

        if self.filename != '':
            self.OG_image = read_image_uint8(self.filename)
            self.LEDsdetected = False
            self.zoomStep = 0

            self.TitleLabel.setText(caliID)
            self.setPhoto(self.OG_image)
        
            self.overview.calibrationProgress(caliID = self.caliID)

            self.setParaDisabled(False)
            self.caliButton.setDisabled(True)

    def setPhoto(self, image):
        self.tmp = image
        frame = image
        if len(image.shape) == 3:
            image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        elif len(image.shape) == 2:
            image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_Indexed8)
        self.previewLabel.setPixmap(QPixmap.fromImage(image))
    

    def showBlurrImage(self):
        tmp = self.OG_image.copy()
        blured = cv2.medianBlur(tmp, self.blurrValue)
        self.setPhoto(blured)
    
    def showPhoto(self):
        self.setPhoto(self.OG_image)


    def setBlurrValue(self):
        if self.blurrSlider.value() % 2 == 0:
            self.blurrValue = self.blurrSlider.value() + 1
        else:
            self.blurrValue = self.blurrSlider.value()

    def detectWells(self):
        tmp = self.OG_image.copy()
        tmp_color = np.stack((tmp,)*3, axis=-1)

        blured = cv2.medianBlur(tmp, self.blurrValue)
        edged = cv2.Canny(blured, 20, 150)
        self.contours = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.contours = imutils.grab_contours(self.contours)
        self.contours = sorted(self.contours, key=cv2.contourArea, reverse=True)[:96]  

        self.wellAmount = len(self.contours)

        cv2.drawContours(tmp_color, self.contours, -1, (255, 150, 100), 2)
        
        self.contours = sort_contours(self.contours, method="left-to-right")

        for i, c in enumerate(self.contours):
            try:
                tmp_color = draw_contour(tmp_color, c, i)
            except:
                pass
        
        if self.wellAmount != self.platetype:
            boxStart = (50, int(tmp.shape[0]/2 - 75))
            boxEnd = (tmp.shape[1] - 50, int(tmp.shape[0]/2 + 75))
            text1Start = (boxStart[0] + 60, boxStart[1] + 40)
            text2Start = (boxStart[0] + 63, boxStart[1] + 75)
            text3Start = (boxStart[0] + 60, boxStart[1] + 110)
            cv2.rectangle(tmp_color, boxStart, boxEnd, (255, 255, 255), -1)
            cv2.putText(tmp_color, "Wells not", 
                    text1Start, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(tmp_color, "detected", 
                    text2Start, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(tmp_color, "correctly!", 
                    text3Start, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        else:
            self.caliButton.setDisabled(False)

        self.setPhoto(tmp_color)


    def calibratePlate(self):
        tmp = self.OG_image.copy()
        tmp_color = np.stack((tmp,)*3, axis=-1)

        meanInts = []

        for c in self.contours:
            wellRadius, wellMid, wellMean = calibrate(c, tmp)
            cv2.circle(tmp_color, wellMid, wellRadius, (255, 150, 100), cv2.FILLED)
            meanInts.append(wellMean)
        
        meanInts = np.array(meanInts)

        if meanInts.shape[0] == 96:
            rows = 12
            cols = 8
        elif meanInts.shape[0] == 24:
            rows = 6
            cols = 4
        elif meanInts.shape[0] == 6:
            rows = 3
            cols = 2

        meanInts = meanInts.reshape(cols, rows)
        meanInts = meanInts.transpose()

        Kis = []
        for y in range(rows):
            KiRow = []
            for x in range(cols):
                Ki = np.min(meanInts)/meanInts[y, x]
                KiRow.append(Ki)
            Kis.append(KiRow)
        Kis = np.array(Kis)

        IntsCV = round(np.std(meanInts)/np.mean(meanInts), 4)
        IntsMean = round(np.mean(meanInts), 4)
        IntsStd = round(np.std(meanInts), 4)

        self.caliKi[self.caliID] = Kis

        boxStart = (50, int(tmp.shape[0]/2 - 75))
        boxEnd = (tmp.shape[1] - 50, int(tmp.shape[0]/2 + 75))

        textDoneStart = (boxStart[0] + 10, boxStart[1] + 30)
        textMeanStart = (boxStart[0] + 56, boxStart[1] + 65)
        textStdStart = (boxStart[0] + 75, boxStart[1] + 95)
        textCVStart = (boxStart[0] + 75, boxStart[1] + 125)
        cv2.rectangle(tmp_color, boxStart, boxEnd, (255, 255, 255), -1)
        cv2.putText(tmp_color, "Calibration Done!", 
                    textDoneStart, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(tmp_color, "Mean: {}".format(IntsMean), 
                    textMeanStart, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(tmp_color, "SD: {}".format(IntsStd), 
                    textStdStart, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(tmp_color, "CV: {}".format(IntsCV), 
                    textCVStart, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        self.overview.setCalibrated(self.caliID, True)
        self.overview.calibrationProgress(self.caliID, True)
        self.setPhoto(tmp_color)

    def resetAll(self):
        alreadyCali = False

        for caliID in self.caliKi.values():
            if caliID is not None:
                alreadyCali = True
                break
        
        if alreadyCali:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("You already made calibrations.")
            msgBox.setInformativeText("Are you sure you want to reset all?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Cancel)

            returnvalue = msgBox.exec()

            if returnvalue == QMessageBox.Yes:
                for caliID in self.caliKi.keys():
                    self.overview.setCalibrated(caliID, False)
                    self.overview.calibrationProgress(caliID, True)
                    self.caliKi[caliID] = None
