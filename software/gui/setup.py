
import sys
import os
import time
import numpy as np

import ast

from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

from mainWidget import *
from create_image import *
from settings import *
from calibrationGUI import *
from progress_bar import *
from makegif import *

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  
    myappid = 'ETHZ.DIYA.DIYA.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

    
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.file_name = 'Untitled'
        self.setWindowTitle('OptoGUI - ' + self.file_name)
        self.setWindowIcon(QIcon(os.path.join(basedir, 'resources', 'DIYA_icon.svg')))

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._connectActions()
        self._createStatusBar()

        self.imageType = 'wellplate'
        self.TopLeftLED = {0: (15, 4), 1: (15, 37)}
        self.LEDmatrixSize = (64, 64)
        self.framerate = 1/60

        self.customPattern = None

        self.caliKi = {}
        for color in ['R', 'G', 'B']:
            for plateType in ['96', '24', '6']:
                for plateNr in ['1', '2']:
                    self.caliKi[str(color + '-' + plateType + '-' + plateNr)] = None
        self.caliKi['TL'] = self.TopLeftLED.copy()

        self.centralWidget = well_buttons(self.framerate)
        self.setCentralWidget(self.centralWidget)

        self.calibrationWindow = None
        self.settingsWindow = None

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        # Separator
        fileMenu.addSeparator()
        fileMenu.addAction(self.exportImgAction)
        fileMenu.addAction(self.exportFramesAction)
        fileMenu.addAction(self.exportVideoAction)
        # Separator
        fileMenu.addSeparator()
        fileMenu.addAction(self.exportCaliDataAction)
        fileMenu.addAction(self.importCaliDataAction)
        fileMenu.addAction(self.exportSettingsAction)
        fileMenu.addAction(self.importSettingsAction)
        # Separator
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        editMenu.addSeparator()
        editMenu.addAction(self.calibrationAction)
        editMenu.addAction(self.settingsAction)

    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.setMovable(False)
        fileToolBar.addAction(self.newAction)
        fileToolBar.addAction(self.openAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addSeparator()
        fileToolBar.addAction(self.exportImgAction)
        fileToolBar.addAction(self.exportFramesAction)
        fileToolBar.addAction(self.exportVideoAction)
        fileToolBar.addSeparator()
        # Edit toolbar
        editToolBar = self.addToolBar("Edit")
        editToolBar.setMovable(False)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.cutAction)
        editToolBar.addSeparator()
        # Calibration toolbar
        settingsToolBar = self.addToolBar("Settings")
        settingsToolBar.setMovable(False)
        settingsToolBar.addAction(self.settingsAction)
        settingsToolBar.addAction(self.calibrationAction)

        spacer_exp = QWidget()
        spacer_exp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        settingsToolBar.addWidget(spacer_exp)

        self.logoPixmap = QPixmap(os.path.join(basedir, 'resources', 'DIYA_full.svg'))
        self.logoLabel = QLabel()
        self.logoLabel.setPixmap(self.logoPixmap)
        settingsToolBar.addWidget(self.logoLabel)

    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        # Temporary message
        self.statusbar.showMessage("Ready", 3000)

    def _createActions(self):
        # File actions
        self.newAction = QAction(QIcon(os.path.join(basedir, 'resources', 'file-new.svg')), "&New", self)
        self.openAction = QAction(QIcon(os.path.join(basedir, 'resources', 'file-open.svg')), "&Open...", self)
        self.saveAction = QAction(QIcon(os.path.join(basedir, 'resources', 'file-save.svg')), "&Save", self)
        self.saveAsAction = QAction(QIcon(os.path.join(basedir, 'resources', 'file-save.svg')), "&Save As", self)
        self.exportFramesAction = QAction(QIcon(os.path.join(basedir, 'resources', 'export-image.svg')), "&Export frames", self)
        self.exportVideoAction = QAction(QIcon(os.path.join(basedir, 'resources', 'export-video.svg')), "&Export video", self)
        self.exportImgAction = QAction(QIcon(os.path.join(basedir, 'resources', 'export-single-image.svg')), "&Export image", self)
        self.exportCaliDataAction = QAction(QIcon(os.path.join(basedir, 'resources', 'export-calibration.svg')), "&Export calibration data", self)
        self.exportSettingsAction = QAction(QIcon(os.path.join(basedir, 'resources', 'export-settings.svg')), "&Export advanced settings (Positioning)", self)
        self.importCaliDataAction = QAction(QIcon(os.path.join(basedir, 'resources', 'import-calibration.svg')), "&Import Calibration Data", self)
        self.importSettingsAction = QAction(QIcon(os.path.join(basedir, 'resources', 'import-settings.svg')), "&Import advanced settings (Positioning)", self)

        self.exitAction = QAction("&Exit", self)
        # Edit actions
        self.copyAction = QAction(QIcon(os.path.join(basedir, 'resources', 'edit-copy.svg')), "&Copy", self)
        self.pasteAction = QAction(QIcon(os.path.join(basedir, 'resources', 'edit-paste.svg')), "&Paste", self)
        self.cutAction = QAction(QIcon(os.path.join(basedir, 'resources', 'edit-cut.svg')), "&Cut", self)
        self.calibrationAction = QAction(QIcon(os.path.join(basedir, 'resources', 'edit-calibration.svg')), "&Calibrate", self)
        self.settingsAction = QAction(QIcon(os.path.join(basedir, 'resources', 'edit-settings.svg')), "&Settings", self)

        # Help tips
        newTip = "Create a new file"
        self.newAction.setStatusTip(newTip)
        self.newAction.setToolTip(newTip)
        saveTip = "Save file"
        self.saveAction.setStatusTip(saveTip)
        self.saveAction.setToolTip(saveTip)
        openTip = "Open an existing file"
        self.openAction.setStatusTip(openTip)
        self.openAction.setToolTip(openTip)
        exportImgTip = "Export selected Step as Image"
        self.exportImgAction.setStatusTip(exportImgTip)
        self.exportImgAction.setToolTip(exportImgTip)
        exportFrameTip = "Export programm as frames"
        self.exportFramesAction.setStatusTip(exportFrameTip)
        self.exportFramesAction.setToolTip(exportFrameTip)
        exportVideoTip = "Export programm as video"
        self.exportVideoAction.setStatusTip(exportVideoTip)
        self.exportVideoAction.setToolTip(exportVideoTip)
        exportCaliTip = "Export calibration Data"
        self.exportCaliDataAction.setStatusTip(exportCaliTip)
        exportSettingsTip = "Export advanced settings Data"
        self.exportSettingsAction.setStatusTip(exportSettingsTip)
        importCaliTip = "Import calibration Data"
        self.importCaliDataAction.setStatusTip(importCaliTip)
        importSettingsTip = "Import advanced settings Data"
        self.importSettingsAction.setStatusTip(importSettingsTip)
        copyTip = "Copy"
        self.copyAction.setStatusTip(copyTip)
        self.copyAction.setToolTip(copyTip)
        pasteTip = "Paste"
        self.pasteAction.setStatusTip(pasteTip)
        self.pasteAction.setToolTip(pasteTip)
        cutTip = "Cut"
        self.cutAction.setStatusTip(cutTip)
        self.cutAction.setToolTip(cutTip)
        calibrationTip = "Calibrate LED Matrix"
        self.calibrationAction.setStatusTip(calibrationTip)
        self.calibrationAction.setToolTip(calibrationTip)
        settingsTip = "Open advanced settings"
        self.settingsAction.setStatusTip(settingsTip)
        self.settingsAction.setToolTip(settingsTip)

        # Shortcuts
        self.copyAction.setShortcut(QKeySequence.Copy)
        self.pasteAction.setShortcut(QKeySequence.Paste)
        self.cutAction.setShortcut(QKeySequence.Cut)
        self.newAction.setShortcut("Ctrl+N")
        self.openAction.setShortcut("Ctrl+O")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAsAction.setShortcut("Shift+Ctrl+S")

    def _connectActions(self):
        # Connect File actions
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.saveAsAction.triggered.connect(self.saveFileAs)
        self.exportFramesAction.triggered.connect(self.exportFrames)
        self.exportVideoAction.triggered.connect(self.exportVideo)
        self.exportImgAction.triggered.connect(self.exportImage)
        self.exportCaliDataAction.triggered.connect(self.exportCalibrationData)
        self.exportSettingsAction.triggered.connect(self.exportSettings)
        self.importCaliDataAction.triggered.connect(self.importCalibrationData)
        self.importSettingsAction.triggered.connect(self.importSettings)
        self.exitAction.triggered.connect(self.close)
        # Connect Edit actions
        self.copyAction.triggered.connect(self.copyContent)
        self.pasteAction.triggered.connect(self.pasteContent)
        self.cutAction.triggered.connect(self.cutContent)
        self.calibrationAction.triggered.connect(self.calibration)
        self.settingsAction.triggered.connect(self.settings)

    # Slots

    #SAVE/NEW/OPEN

    def checkforChanges(self):
        caliKiList = {}
        for caliID in self.caliKi.keys():
            if caliID == 'TL':
                caliKiList[caliID] = self.caliKi[caliID].copy()
            else:
                caliKiList[caliID] = self.caliKi[caliID] if self.caliKi[caliID] is None else self.caliKi[caliID].tolist()
        testsave = {
        'plateInfo': self.centralWidget.getPlateInfo().copy(),
        'caliKi': caliKiList.copy(),
        'TL': self.TopLeftLED.copy(),
        'imageType': self.imageType,
        'shape': self.customPattern if self.customPattern is None else self.customPattern.tolist()}
        caliKiBlank = {}
        for color in ['R', 'G', 'B']:
            for plateType in ['96', '24', '6']:
                for plateNr in ['1', '2']:
                    caliKiBlank[str(color + '-' + plateType + '-' + plateNr)] = None
        caliKiBlank['TL'] = {0: (15, 4), 1: (15, 37)}
        blanksave = {
        'plateInfo': {1: [[0, 10, 0], {'Plate 1 Wells': {}, 'Plate 1 Type': 96, 'Plate 2 Wells': {}, 'Plate 2 Type': 96}]}, 
        'caliKi': caliKiBlank,
        'TL': {0: (15, 4), 1: (15, 37)}, 
        'imageType': 'wellplate', 
        'shape': None}
        
        def showSaveDialog():
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("The document has been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)

            returnvalue = msgBox.exec()

            if returnvalue == QMessageBox.Save:
                self.saveFile()
                return True
            if returnvalue == QMessageBox.Discard:
                return True
            if returnvalue == QMessageBox.Cancel:
                return False

        if str(testsave) == str(blanksave):
            return True
        elif self.file_name != 'Untitled': 
            file = open(self.file_name, "r")
            saved_changes = file.read()
            file.close()
            if saved_changes != str(testsave):
                stillcontinue = showSaveDialog()
                return stillcontinue
            else:
                return True
        else: 
            stillcontinue = showSaveDialog()
            return stillcontinue

    def newFile(self):
        if self.checkforChanges():
            self.centralWidget.deleteLater()
            self.centralWidget = well_buttons(self.framerate)
            self.setCentralWidget(self.centralWidget)
            self.imageType = 'wellplate'
            self.TopLeftLED = {0: (15, 6), 1: (15, 36)}
            self.caliKi = {}
            for color in ['R', 'G', 'B']:
                for plateType in ['96', '24', '6']:
                    for plateNr in ['1', '2']:
                        self.caliKi[str(color + '-' + plateType + '-' + plateNr)] = None
            self.caliKi['TL'] = self.TopLeftLED.copy()
            self.customPattern = None
            self.file_name = 'Untitled'
            self.setWindowTitle('OptoGUI - ' + self.file_name)
            self.statusbar.showMessage("Ready", 3000)

    def openFile(self):
        if self.checkforChanges():
            open_file_name = QFileDialog.getOpenFileName(self,
                self.tr("Open file"), "",
                self.tr("OptoGUI files (*.opto)"))[0]
            if open_file_name != '':
                self.file_name = open_file_name

                file = open(self.file_name, "r")
                data_to_load = file.read()
                file.close()

                if not isinstance(data_to_load, dict):
                    data_to_load = ast.literal_eval(data_to_load)

                if self.settingsWindow is not None:
                    self.settingsWindow.close()
                    self.settingsWindow = None
                if self.calibrationWindow is not None:
                    self.calibrationWindow.close()
                    self.calibrationWindow = None

                self.centralWidget.deleteLater()
                self.centralWidget = well_buttons(self.framerate)
                self.setCentralWidget(self.centralWidget)

                plateInfo = data_to_load['plateInfo']
                self.caliKi = {}

                for caliID in data_to_load['caliKi'].keys():
                    if caliID == 'TL':
                        self.caliKi[caliID] = data_to_load['caliKi'][caliID].copy()
                    else:
                        self.caliKi[caliID] = data_to_load['caliKi'][caliID] if data_to_load['caliKi'][caliID] is None else np.array(data_to_load['caliKi'][caliID])
                self.TopLeftLED = data_to_load['TL']
                oldimageType = self.imageType
                self.imageType = data_to_load['imageType']
                self.customPattern = np.array(data_to_load['shape']) if isinstance(data_to_load['shape'], list) else data_to_load['shape']

                if oldimageType != self.imageType:
                    self.centralWidget.changeShape(self.imageType)

                self.centralWidget.loadPlateInfo(plateInfo)

                self.setWindowTitle('OptoGUI - ' + os.path.basename(self.file_name))
                self.statusbar.showMessage(self.file_name, 3000)


    def saveFile(self):
        caliKiList = {}
        for caliID in self.caliKi.keys():
            if caliID == 'TL':
                caliKiList[caliID] = self.caliKi[caliID].copy()
            else:
                caliKiList[caliID] = self.caliKi[caliID] if self.caliKi[caliID] is None else self.caliKi[caliID].tolist()
        saveInfo = {
        'plateInfo': self.centralWidget.getPlateInfo().copy(),
        'caliKi': caliKiList,
        'TL': self.TopLeftLED.copy(),
        'imageType': self.imageType,
        'shape': self.customPattern if self.customPattern is None else self.customPattern.tolist()
        }
        if self.file_name == 'Untitled':
            self.saveFileAs()
        else:
            file = open(self.file_name,'w')
            file.write(str(saveInfo))
            file.close()
            self.statusbar.showMessage('File saved under {}'.format(self.file_name), 3000)

    def saveFileAs(self):
        caliKiList = {}
        for caliID in self.caliKi.keys():
            if caliID == 'TL':
                caliKiList[caliID] = self.caliKi[caliID].copy()
            else:
                caliKiList[caliID] = self.caliKi[caliID] if self.caliKi[caliID] is None else self.caliKi[caliID].tolist()
        saveInfo = {
        'plateInfo': self.centralWidget.getPlateInfo().copy(),
        'caliKi': caliKiList,
        'TL': self.TopLeftLED.copy(),
        'imageType': self.imageType,
        'shape': self.customPattern if self.customPattern is None else self.customPattern.tolist()
        }
        self.choosen_file_name = QFileDialog.getSaveFileName(self,
            self.tr("Save file"), "",
            self.tr("OptoGUI files (*.opto)"))[0]
        if self.choosen_file_name != '':
            self.file_name = self.choosen_file_name
            file = open(self.file_name,'w')
            file.write(str(saveInfo))
            file.close()
            self.setWindowTitle('OptoGUI - ' + os.path.basename(self.file_name))
            self.statusbar.showMessage('File saved under {}'.format(self.file_name), 3000)

    # Settings Export / Import

    def exportCalibrationData(self):
        caliKiList = {}
        for caliID in self.caliKi.keys():
            if caliID == 'TL':
                caliKiList[caliID] = self.caliKi[caliID].copy()
            else:
                caliKiList[caliID] = self.caliKi[caliID] if self.caliKi[caliID] is None else self.caliKi[caliID].tolist()
        self.choosen_file_name = QFileDialog.getSaveFileName(self,
            self.tr("Save file"), "",
            self.tr("OptoGUI Calibration files (*.optocal)"))[0]
        if self.choosen_file_name != '':
            self.file_name = self.choosen_file_name
            file = open(self.file_name,'w')
            file.write(str(caliKiList))
            file.close()
            self.statusbar.showMessage('File saved under {}'.format(self.file_name), 3000)

    def exportSettings(self, exportShapeButton = False):
        if exportShapeButton:
            settingsInfo = {
            'TL': self.settingsWindow.TopLeftLED,
            'imageType': self.settingsWindow.imageType,
            'shape': self.settingsWindow.previewArr.tolist()
            }
        else:
            settingsInfo = {
            'TL': self.TopLeftLED.copy(),
            'imageType': self.imageType,
            'shape': self.customPattern if self.customPattern is None else self.customPattern.tolist()
            }
        self.choosen_file_name = QFileDialog.getSaveFileName(self,
            self.tr("Save file"), "",
            self.tr("OptoGUI Settings files (*.optoset)"))[0]
        if self.choosen_file_name != '':
            self.file_name = self.choosen_file_name
            file = open(self.file_name,'w')
            file.write(str(settingsInfo))
            file.close()
            self.statusbar.showMessage('File saved under {}'.format(self.file_name), 3000)

    def importCalibrationData(self):
        open_file_name = QFileDialog.getOpenFileName(self,
            self.tr("Open file"), "",
            self.tr("OptoGUI calibration files (*.optocal)"))[0]
        if open_file_name != '':
            self.file_name = open_file_name

            file = open(self.file_name, "r")
            data_to_load = file.read()
            file.close()

            if not isinstance(data_to_load, dict):
                data_to_load = ast.literal_eval(data_to_load)

            if self.calibrationWindow is not None:
                self.calibrationWindow.close()

            importCaliKi = {}
            for caliID in data_to_load.keys():
                if caliID == 'TL':
                    importCaliKi[caliID] = data_to_load[caliID].copy()
                else:
                    importCaliKi[caliID] = data_to_load[caliID] if data_to_load[caliID] is None else np.array(data_to_load[caliID])

            if importCaliKi['TL'] != self.TopLeftLED:
                msgBox = QMessageBox()
                msgBox.setText("Calibration for diffrent LED Positioning")
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setInformativeText('The imported calibration succeeded for other plate positions.  If you continue, your plates will be moved to the corresponding position.  Do you still want to continue?')
                msgBox.addButton(QMessageBox.No)
                msgBox.addButton(QMessageBox.Yes)
                bttn = msgBox.exec_()

                if bttn == QMessageBox.Yes:
                    self.TopLeftLED = importCaliKi['TL'].copy()
                elif bttn == QMessageBox.No:
                    return
            
            self.caliKi = importCaliKi.copy()

            if self.settingsWindow is not None:
                self.settingsWindow.close()
                self.settingsWindow = None
            if self.calibrationWindow is not None:
                self.calibrationWindow.close()
                self.calibrationWindow = None

            self.statusbar.showMessage('Imported {self.file_name} successfully!', 3000)

    def importSettings(self, importShapeButton = False):
        open_file_name = QFileDialog.getOpenFileName(self,
            self.tr("Open file"), "",
            self.tr("OptoGUI settings files (*.optoset)"))[0]
        if open_file_name != '':
            self.file_name = open_file_name

            file = open(self.file_name, "r")
            data_to_load = file.read()
            file.close()

            if not isinstance(data_to_load, dict):
                data_to_load = ast.literal_eval(data_to_load)

            if data_to_load['imageType'] != self.imageType and not importShapeButton:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('The currently used pattern type ({old}) does not match the one in the settings file ({new}).'.format(old = self.imageType, new = data_to_load['imageType']))
                msg.setWindowTitle("Error")
                msg.exec_()
                imageTypeError = True
            else:
                imageTypeError = False

            if not imageTypeError or importShapeButton:
                if data_to_load['imageType'] == 'wellplate' and data_to_load['TL'] != self.TopLeftLED:
                    noCali = True
                    for key, value in self.caliKi.items():
                        if key != 'TL':
                            if value is not None:
                                noCali = False
                    if not noCali:
                        msgBox = QMessageBox()
                        msgBox.setText("Calibration for diffrent LED Positioning")
                        msgBox.setIcon(QMessageBox.Warning)
                        msgBox.setInformativeText('A calibration has already been performed for the old plate positions.  If you change the position, all previous calibration data will be reset.  Do you still want to continue?')
                        msgBox.addButton(QMessageBox.No)
                        msgBox.addButton(QMessageBox.Yes)

                        bttn = msgBox.exec_()

                        if bttn == QMessageBox.Yes:
                            changeTL = True
                        elif bttn == QMessageBox.No:
                            return
                    else:
                        changeTL = True
                    
                    if changeTL:
                        self.TopLeftLED = data_to_load['TL'].copy()
                        #self.framerate = self.settingsWindow.framerate
                        #self.centralWidget.settingsChanged(self.framerate)
                        self.imageType = data_to_load['imageType']
                        self.customPattern = np.array(data_to_load['shape']) if isinstance(data_to_load['shape'], list) else data_to_load['shape']
                        self.caliKi = {}
                        for color in ['R', 'G', 'B']:
                            for plateType in ['96', '24', '6']:
                                for plateNr in ['1', '2']:
                                    self.caliKi[str(color + '-' + plateType + '-' + plateNr)] = None
                        self.caliKi['TL'] =  data_to_load['TL'].copy()
                elif importShapeButton:
                    newPattern = np.array(data_to_load['shape']) if isinstance(data_to_load['shape'], list) else data_to_load['shape']
                    self.settingsWindow.importData(data_to_load['imageType'], TL = self.TopLeftLED, customPattern = newPattern)
                else:
                    self.TopLeftLED = data_to_load['TL']
                    self.imageType = data_to_load['imageType']
                    self.customPattern = np.array(data_to_load['shape']) if isinstance(data_to_load['shape'], list) else data_to_load['shape']

                if not importShapeButton:
                    if self.settingsWindow is not None:
                        self.settingsWindow.close()
                        self.settingsWindow = None
                    if self.calibrationWindow is not None:
                        self.calibrationWindow.close()
                        self.calibrationWindow = None
                self.statusbar.showMessage('Imported {self.file_name} successfully!', 3000)

    #EXPORT
    def exportFrames(self):
        StepInformations = self.centralWidget.getPlateInfo()

        path = QFileDialog.getSaveFileName(self,
            self.tr("Export Frames"), "",
            self.tr(""))[0]
        if path != '':
            if not os.path.isdir(path):
                os.mkdir(path)
            else:
                timestr = time.strftime("%Y%m%d-%H%M%S")
                path = path + '/' + timestr
                os.mkdir(path)
            if self.imageType == 'wellplate':
                customShape = None
            elif self.imageType == 'custompattern':
                customShape = self.customPattern
            createFrames(StepInformations, self.TopLeftLED, self.framerate, path, self.caliKi, customShape = customShape)
            QMessageBox.about(self, "Success!", "Frames has been created and saved under {}".format(path))
         
    def exportVideo(self):
        StepInformations = self.centralWidget.getPlateInfo()

        GIFfilename = QFileDialog.getSaveFileName(self,
            self.tr("Export Video"), "",
            self.tr("Video Files (*.gif)"))[0]

        if GIFfilename != '':
            if self.imageType == 'wellplate':
                customShape = None
            elif self.imageType == 'custompattern':
                customShape = self.customPattern
            
            self.progressBar = progressBarWidget()
            self.progressBar._close.connect(self.closeProgressbar)
            self.progressBar.show()

            GIFframes, GIFfps = createVideo(StepInformations, self.TopLeftLED, self.framerate, GIFfilename, self.caliKi, customShape = customShape)
            
            self.mkGifcount = 0
            self.mkGifonePer = GIFframes.shape[0] * 3 // 100
            self.mkGifPer = 0
            
            self.mkGifThread = QThread()
            self.mkGifWorker = makeGifObj()

            self.mkGifWorker.moveToThread(self.mkGifThread)

            self.mkGifThread.started.connect(lambda: self.mkGifWorker.write_gif(GIFframes, GIFfilename, fps = GIFfps))
            self.mkGifThread.finished.connect(self.mkGifThread.deleteLater)
            self.mkGifWorker._done.connect(self.mkGifThread.quit)
            self.mkGifWorker._done.connect(self.mkGifWorker.deleteLater)
            self.mkGifWorker._done.connect(self.finishExport)
            self.mkGifWorker._progress.connect(self.reportProgress)

            self.mkGifThread.start()
    def reportProgress(self, filename):
        self.mkGifcount += 1

        if self.mkGifPer < 10 and self.mkGifPer > 4:
            self.progressBar.infoLabel.setText("Creating array from GUI data...")
        elif self.mkGifPer < 20 and self.mkGifPer >= 10:
            self.progressBar.infoLabel.setText("Checking Data...")
        elif self.mkGifPer < 41 and self.mkGifPer >= 20:
            self.progressBar.infoLabel.setText("Creating Images...")
        elif self.mkGifPer < 62 and self.mkGifPer >= 41:
            self.progressBar.infoLabel.setText("Creating GIF...")
        elif self.mkGifPer < 88 and self.mkGifPer >= 62:
            self.progressBar.infoLabel.setText("Writing data to file...")
        elif self.mkGifPer < 98 and self.mkGifPer >= 88:
            self.progressBar.infoLabel.setText("Finalize the processing...")
        elif self.mkGifPer >= 99:
            self.progressBar.progress.setValue(99)
            self.progressBar.progressLabel.setText('{p} %'.format(p = 99))

        if self.mkGifcount >= self.mkGifonePer and self.mkGifPer < 99:
            self.mkGifPer += 1
            self.mkGifcount = 0
            self.progressBar.progress.setValue(int(self.mkGifPer))
            self.progressBar.progressLabel.setText('{p} %'.format(p = self.mkGifPer))
        
        QApplication.processEvents() 
    def finishExport(self):
        self.progressBar.progress.setValue(100)
        time.sleep(1)
        self.progressBar.progressLabel.setText('{p} %'.format(p = 100))
        self.progressBar.titleLabel.setText('Done!')
        self.progressBar.infoLabel.setText("The GIF has been created!")
        self.progressBar.stackBar.setCurrentIndex(1)
        self.progressBar.progressLabel.setText('')
    def closeProgressbar(self, closetype):
        if closetype == 1:
            self.progressBar.close()
        self.progressBar = None
        self.mkGifcount = None
        self.mkGifonePer = None
        self.mkGifPer = None

    def exportImage(self):
        StepInformations = self.centralWidget.getStepInfo()
        maxIntensity = True
        minIntensity = False
        for step in StepInformations['Plate 1 Wells']:
            if StepInformations['Plate 1 Wells'][step]['waveType'] in {'sin', 'tri', 'sq', 'rise', 'fall'}:
                minIntensity = True
        for step in StepInformations['Plate 2 Wells']:
            if StepInformations['Plate 2 Wells'][step]['waveType'] in {'sin', 'tri', 'sq', 'rise', 'fall'}:
                minIntensity = True

        if minIntensity:
                msgBox = QMessageBox()
                msgBox.setText("Choose Intensity for Export")
                msgBox.setIcon(QMessageBox.Question)
                msgBox.setInformativeText('At least one of the wells in this step are animated.  Do you want to use the maximum or minimum value for this well(s)?')
                maxbutton = msgBox.addButton('Use maximum', QMessageBox.YesRole)
                msgBox.setDefaultButton(maxbutton)
                minbutton = msgBox.addButton('Use minimum', QMessageBox.NoRole)
                msgBox.addButton(QMessageBox.Cancel)

                bttn = msgBox.exec_()

                if msgBox.clickedButton() == maxbutton:
                    maxIntensity = True
                elif msgBox.clickedButton() == minbutton:
                    maxIntensity = False
                elif bttn == QMessageBox.Cancel:
                    return


        filename = QFileDialog.getSaveFileName(self,
            self.tr("Export Image"), "",
            self.tr("Tiff file (*.tiff *.tif)"))[0]
        if filename != '':
            if self.imageType == 'wellplate':
                customShape = None
            elif self.imageType == 'custompattern':
                customShape = self.customPattern
            createImage(StepInformations, self.TopLeftLED, filename, self.caliKi, maxIntensity, customShape = customShape)
            QMessageBox.about(self, "Success!", "The image has been created and saved under {}".format(filename))

    #COPY / PASTE 

    def copyContent(self):
        self.centralWidget.copy_wells()

    def pasteContent(self):
        self.centralWidget.paste_wells()

    def cutContent(self):
        self.centralWidget.cut_wells()

    #SETTINGS

    def calibration(self):
        if self.calibrationWindow is None:
            caliKi = self.caliKi.copy()
            del caliKi['TL']
            self.calibrationWindow = calibrationWindow(caliKi)
            self.calibrationWindow.getCaliData.connect(self.saveCalibration)
            self.calibrationWindow.cancelCali.connect(self.cancelCalibration)
            self.calibrationWindow.show()
        else:
            self.saveCalibration()
            self.calibrationWindow = None

    def saveCalibration(self):
        self.caliKi = self.calibrationWindow.caliKi.copy()
        self.caliKi['TL'] = self.TopLeftLED.copy()
        self.calibrationWindow.close()

        self.calibrationWindow = None

    def cancelCalibration(self):
        self.calibrationWindow = None

    def settings(self):
        if self.settingsWindow is None:
            if self.imageType == 'wellplate':
                self.settingsWindow = settingsWindow(self.LEDmatrixSize, self.framerate, self.imageType, TL = self.TopLeftLED, plateNrType = self.centralWidget.plate_nr_type)
            elif self.imageType == 'custompattern':
                self.settingsWindow = settingsWindow(self.LEDmatrixSize, self.framerate, self.imageType, TL = self.TopLeftLED, customPattern = self.customPattern)
            self.settingsWindow.saveSettings.connect(self.saveSettings)
            self.settingsWindow.cancelSettings.connect(self.cancelSettings)
            self.settingsWindow.importShape.connect(lambda save = True: self.importSettings(importShapeButton = save))
            self.settingsWindow.exportShape.connect(lambda save = True: self.exportSettings(exportShapeButton = save))
            self.settingsWindow.show()
        else: 
            self.saveSettings()

    def saveSettings(self):
        oldImageType = self.imageType

        newTopLeftLED = self.settingsWindow.TopLeftLED
        #self.framerate = self.settingsWindow.framerate
        #self.centralWidget.settingsChanged(self.framerate)
        newImageType = self.settingsWindow.imageType
        newCustomPattern = self.settingsWindow.previewArr

        self.settingsWindow.close()
        self.settingsWindow = None

        if newImageType == 'wellplate':
            if newTopLeftLED != self.caliKi['TL']:
                noCali = True
                for key, value in self.caliKi.items():
                    if key != 'TL':
                        if value is not None:
                            noCali = False
                if not noCali:
                    msgBox = QMessageBox()
                    msgBox.setText("Calibration for diffrent LED Positioning")
                    msgBox.setIcon(QMessageBox.Warning)
                    msgBox.setInformativeText('A calibration has already been performed for the old plate positions.  If you change the position,  all previous calibration data will be reset.  Do you still want to continue?')
                    msgBox.addButton(QMessageBox.No)
                    msgBox.addButton(QMessageBox.Yes)

                    bttn = msgBox.exec_()

                    if bttn == QMessageBox.Yes:
                        changeTL = True
                    elif bttn == QMessageBox.No:
                        return
                else:
                    changeTL = True
                
                if changeTL:
                    self.TopLeftLED = newTopLeftLED.copy()
                    #self.framerate = self.settingsWindow.framerate
                    #self.centralWidget.settingsChanged(self.framerate)
                    self.imageType = newImageType
                    self.customPattern = newCustomPattern
                    self.caliKi = {}
                    for color in ['R', 'G', 'B']:
                        for plateType in ['96', '24', '6']:
                            for plateNr in ['1', '2']:
                                self.caliKi[str(color + '-' + plateType + '-' + plateNr)] = None
                    self.caliKi['TL'] = newTopLeftLED.copy()
            else:
                self.TopLeftLED = newTopLeftLED.copy()
                #self.framerate = self.settingsWindow.framerate
                #self.centralWidget.settingsChanged(self.framerate)
                self.imageType = newImageType
                self.customPattern = newCustomPattern
        else:
            self.imageType = newImageType 
            self.customPattern = newCustomPattern

        if newImageType != oldImageType:
                self.centralWidget.changeShape(self.imageType)

    def cancelSettings(self):
        self.settingsWindow = None
        
    #Events
    def closeEvent(self, event):
        close = self.checkforChanges()
        if close:
            if self.settingsWindow is not None:
                self.settingsWindow.close()
            if self.calibrationWindow is not None:
                self.calibrationWindow.close()
            if self.centralWidget.wellInfoWin is not None:
                self.centralWidget.wellInfoWin.close()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



