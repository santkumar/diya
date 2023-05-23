from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import ast
import os

import numpy as np
from math import sqrt

from wellInforamtion import wellInfoWindow

basedir = os.path.dirname(__file__)

class well_buttons(QWidget):#
    #Creation of widgets
    def __init__(self, framerate):
        super().__init__()

        self.plate_type = 96
        self.plate_nr = 0

        self.plate_nr_type = {0: 96, 1: 96}

        self.plate_width = 8
        self.plate_height = 12
        self.well_button_size = 30
        self.well_button_radius = 15

        self.color = 'Off'
        self.wvMax = 255
        self.wvMin = 0
        self.wvStart = 'Low'
        self.wvLen = 10
        self.dutyCyclePWM = 0.5
        self.periodPWM = 10

        self.framerate = framerate

        self.StepGBoxes = {}
        self.StepInformations = {}
        self.amount_of_steps = 1
        self.selceted_step = 1

        self.ButtonNrTL = 1
        self.selected_wells = set()
        self.used_wells_plate_1 = {}
        self.used_wells_plate_2 = {}
        self.Button_to_pos = {}
        self.Pos_to_Button = {}

        self.plotPreviewDisplayed = False
        self.wellInfoWin = None
        
        self.setWindowTitle('opto GUI')
        self.createPlotPreview(10)
        self.createPlateChooserBox()
        self.createCurrentStepBox()
        self.createProgrammBox()
        self.createActions()
        self.createContextMenu()
        
        self.selectWellsRB.setChecked(True)

        self.graphProgrammStack = QStackedWidget(self)
        self.graphProgrammStack.addWidget(self.ProgrammGBox)
        self.graphProgrammStack.addWidget(self.graphWidget)

        Programm_HLayout = QVBoxLayout()
        Programm_HLayout.addWidget(self.PlateChooserBox)
        Programm_HLayout.addWidget(self.graphProgrammStack)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(Programm_HLayout)
        self.mainLayout.addWidget(self.CurrentStepGBox)
        self.setLayout(self.mainLayout)

    def createwellButtonBox(self):

        self.wellButtonBox = QGroupBox("Select wells")
        wells_layout = QGridLayout()

        rows_per_plate, cols_per_plate = self.plate_height, self.plate_width

        self.select_buttons = {}
        self.well_buttons = {}
        self.Button_to_pos = {}
        self.Pos_to_Button = {}

        self.select_all_button = QPushButton('All', self)
        self.select_all_button.\
         setStyleSheet("border-radius : {radius}; border: 1px solid black;".format(radius = 15))
        self.select_all_button.setFixedSize(30, 30)
        self.select_all_button.clicked.connect(self.select_all)
        wells_layout.addWidget(self.select_all_button, 0, 0, alignment = Qt.AlignCenter)

        for col in range(cols_per_plate):
            col_nr = col + 1
            self.select_buttons['Button_C' + str(col_nr)] = QPushButton('', self)
            self.select_buttons['Button_C' + str(col_nr)].\
             setStyleSheet("border-radius : {radius}; border: 1px solid black;".format(radius = 15))
            self.select_buttons['Button_C' + str(col_nr)].setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-down.svg')))
            self.select_buttons['Button_C' + str(col_nr)].setFixedSize(30, 30)
            self.select_buttons['Button_C' + str(col_nr)].clicked.connect(lambda ignore, i=col_nr: self.select_col(i))
            wells_layout.addWidget(self.select_buttons['Button_C' + str(col_nr)], 0, col + 1, alignment = Qt.AlignCenter)

        for row in range(rows_per_plate):
            row_nr = row + 1
            self.select_buttons['Button_R' + str(row_nr)] = QPushButton('', self)
            self.select_buttons['Button_R' + str(row_nr)].\
             setStyleSheet("border-radius : {radius}; border: 1px solid black;".format(radius = 15))
            self.select_buttons['Button_R' + str(row_nr)].setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-right.svg')))
            self.select_buttons['Button_R' + str(row_nr)].setFixedSize(30, 30)
            self.select_buttons['Button_R' + str(row_nr)].clicked.connect(lambda ignore, i=row_nr: self.select_row(i))
            wells_layout.addWidget(self.select_buttons['Button_R' + str(row_nr)], row + 1, 0, alignment = Qt.AlignCenter)

        for x in range(cols_per_plate):
            for y in range(rows_per_plate):
                button_nr = x+y*cols_per_plate+1
                self.well_buttons['Button_' + str(button_nr)] = QPushButton('', self)
                self.Button_to_pos['Button_' + str(button_nr)] = (y, x)
                self.well_buttons['Button_' + str(button_nr)].\
                 setStyleSheet("border-radius : {radius}; border: 1px solid black;".format(radius = self.well_button_radius))
                self.well_buttons['Button_' + str(button_nr)].setFixedSize(self.well_button_size, self.well_button_size)
                self.well_buttons['Button_' + str(button_nr)].clicked.connect(lambda ignore, i=button_nr: self.select_wells(i))
                self.well_buttons['Button_' + str(button_nr)].setContextMenuPolicy(Qt.CustomContextMenu)
                self.well_buttons['Button_' + str(button_nr)].customContextMenuRequested.connect(lambda point, i=button_nr: self.showWellContextMenu(i, point))
                wells_layout.addWidget(self.well_buttons['Button_' + str(button_nr)], y+1, x+1)
        self.wellButtonBox.setLayout(wells_layout)
        self.Pos_to_Button = {y: x for x, y in self.Button_to_pos.items()}

    def createPlateChooserBox(self):
        self.PlateChooserBox = QGroupBox("Choose Plate")
        chooserForm_layout = QFormLayout()

        self.plate_chooser_CB = QComboBox()
        self.plate_chooser_CB.addItem("Plate 1")
        self.plate_chooser_CB.addItem("Plate 2")
        self.plate_chooser_CB.addItem("---")

        self.plate_chooser_CBView = self.plate_chooser_CB.view()
        self.plate_chooser_CBView.setRowHidden(2, True)

        self.plate_chooser_CB.currentIndexChanged.connect(self.changePlate)

        self.plate_type_CB = QComboBox()
        self.plate_type_CB.addItem("96-well Plate")
        self.plate_type_CB.addItem("24-well Plate")
        self.plate_type_CB.addItem("6-well Plate")
        self.plate_type_CB.addItem("Custom Shape")

        self.plate_type_CBView = self.plate_type_CB.view()
        self.plate_type_CBView.setRowHidden(3, True)

        self.plate_type_CB.currentIndexChanged.connect(self.changePlateType)

        self.duplicate_plate_button = QPushButton('Duplicate Plate', self)
        self.duplicate_plate_button.clicked.connect(self.duplicate_plate)

        chooserForm_layout.addRow(QLabel('Choose Plate'), self.plate_chooser_CB)
        chooserForm_layout.addRow(QLabel('Choose Plate Type'), self.plate_type_CB)
        chooserForm_layout.addRow(QLabel(''), self.duplicate_plate_button)

        self.PlateChooserBox.setLayout(chooserForm_layout)

    def createParameterBox(self):
        self.ParameterBox = QGroupBox("Animate wells")
        self.ParameterFormlayout = QFormLayout()

        self.color_chooser = QComboBox()
        self.color_chooser.addItem("Off")
        self.color_chooser.addItem("Red")
        self.color_chooser.addItem("Green")
        self.color_chooser.addItem("Blue")
        self.color_chooser.setCurrentText(self.color)
        self.color_chooser.currentIndexChanged.connect(self.changeWavetype)

        self.waveTypeCB = QComboBox()
        self.waveTypeCB.addItem("Constant")
        self.waveTypeCB.addItem("Sine Wave")
        self.waveTypeCB.addItem("Tri Wave")
        self.waveTypeCB.addItem("Square Wave")
        self.waveTypeCB.addItem("PWM")
        self.waveTypeCB.addItem("Rise")
        self.waveTypeCB.addItem("Fall")
        self.waveTypeCB.setItemIcon(0, QIcon(os.path.join(basedir, 'resources', 'animation-static.svg')))
        self.waveTypeCB.setItemIcon(1, QIcon(os.path.join(basedir, 'resources', 'animation-sin.svg')))
        self.waveTypeCB.setItemIcon(2, QIcon(os.path.join(basedir, 'resources', 'animation-tri.svg')))
        self.waveTypeCB.setItemIcon(3, QIcon(os.path.join(basedir, 'resources', 'animation-sq.svg')))
        self.waveTypeCB.setItemIcon(4, QIcon(os.path.join(basedir, 'resources', 'animation-blink.svg')))
        self.waveTypeCB.setItemIcon(5, QIcon(os.path.join(basedir, 'resources', 'animation-rise.svg')))
        self.waveTypeCB.setItemIcon(6, QIcon(os.path.join(basedir, 'resources', 'animation-fall.svg')))
        self.waveTypeCB.currentIndexChanged.connect(self.changeWavetype)

        self.ParameterFormlayout.addRow(QLabel('Color: '), self.color_chooser)
        self.ParameterFormlayout.addRow(QLabel('Type: '), self.waveTypeCB)

        self.ParameterBox.setLayout(self.ParameterFormlayout)

        self.changeWavetype()

    def createGradientDesingerBox(self):
        self.GradientBox = QGroupBox("Gradient")
        gradientForm_layout = QFormLayout()
        gradientSize_layout = QHBoxLayout()

        self.color_chooser_gradient = QComboBox()
        self.color_chooser_gradient.addItem("Red")
        self.color_chooser_gradient.addItem("Green")
        self.color_chooser_gradient.addItem("Blue")

        self.width_gradient = QSpinBox()
        self.width_gradient.setMaximum(self.plate_width)
        self.width_gradient.setMinimum(2)
        self.width_gradient.setValue(8)
        self.width_gradient.valueChanged.connect(lambda: self.select_wells(self.ButtonNrTL))
        self.height_gradient = QSpinBox()
        self.height_gradient.setMaximum(self.plate_height)
        self.height_gradient.setMinimum(2)
        self.height_gradient.setValue(12)
        self.height_gradient.valueChanged.connect(lambda: self.select_wells(self.ButtonNrTL))
        gradientSize_layout.addWidget(self.width_gradient)
        gradientSize_layout.addWidget(QLabel("x"))
        gradientSize_layout.addWidget(self.height_gradient)

        self.direction_chooser_gradient = QComboBox()
        self.direction_chooser_gradient.addItem("Top --> Bottom")
        self.direction_chooser_gradient.addItem("Bottom --> Top")
        self.direction_chooser_gradient.addItem("Left --> Right")
        self.direction_chooser_gradient.addItem("Right --> Left")

        self.max_gradient = QSpinBox()
        self.max_gradient.setMaximum(255)
        self.max_gradient.setValue(255)
        self.min_gradient = QSpinBox()
        self.min_gradient.setMaximum(254)
        self.min_gradient.valueChanged.connect(lambda x: self.max_gradient.setMinimum(self.min_gradient.value() + 1))
        self.max_gradient.valueChanged.connect(lambda x: self.min_gradient.setMaximum(self.max_gradient.value() - 1))

        gradientForm_layout.addRow(QLabel('Color'), self.color_chooser_gradient)
        gradientForm_layout.addRow(QLabel('Size'), gradientSize_layout)
        gradientForm_layout.addRow(QLabel('Direction'), self.direction_chooser_gradient)
        gradientForm_layout.addRow(QLabel('Min. intensity'), self.min_gradient)
        gradientForm_layout.addRow(QLabel('Max. intensity'), self.max_gradient)

        self.apply_button_gradient = QPushButton('Apply', self)
        self.apply_button_gradient.clicked.connect(self.createGradient)
        self.apply_button_gradient.setDefault(True)
        gradientForm_layout.addRow(QLabel(), self.apply_button_gradient)

        self.GradientBox.setLayout(gradientForm_layout)

    def createPlotPreview(self, stepLength):
        self.graphWidget = pg.PlotWidget()
        self.pen = pg.mkPen(color='red', width=2)

        self.graphWidget.setBackground('w')
        self.graphWidget.setLimits(xMin = 0, xMax = stepLength - self.framerate + (stepLength - self.framerate) * 0.05, yMin = -1, yMax = 256, minXRange = 5, minYRange = 25)
        labelStyle = {'color': 'black', 'font-size': '12pt'}
        self.graphWidget.setLabel('bottom', "Time / min", **labelStyle)
        self.graphWidget.setLabel('left', "Intensity", **labelStyle)
        self.graphWidget.setXRange(0, stepLength - self.framerate + (stepLength - self.framerate) * 0.05)
        self.graphWidget.setYRange(0, 260)

        self.data_line =  self.graphWidget.plot([0], [0], pen=self.pen)

    def createCurrentStepBox(self):
        self.CurrentStepGBox = QGroupBox("Step 1")
        self.CurrentStepGBox_Layout = QHBoxLayout()
        Parameter_Layout = QVBoxLayout()
        Preview_select_Layout = QVBoxLayout()

        rb_layout = QHBoxLayout()
        self.selectWellsRB = QRadioButton("Select wells")
        self.selectWellsRB.toggled.connect(lambda: self.changeSelectionType(0))
        rb_layout.addWidget(self.selectWellsRB)
        self.getSettingsRB = QRadioButton("Get Settings")
        self.getSettingsRB.toggled.connect(lambda: self.changeSelectionType(2))
        rb_layout.addWidget(self.getSettingsRB)
        self.createGradientRB = QRadioButton("Create gradient")
        self.createGradientRB.toggled.connect(lambda: self.changeSelectionType(1))
        rb_layout.addWidget(self.createGradientRB)

        self.createwellButtonBox()
        self.createParameterBox()
        self.createGradientDesingerBox()
        
        Parameter_Layout.addLayout(rb_layout)
        Parameter_Layout.addWidget(self.ParameterBox)
        Parameter_Layout.addWidget(self.GradientBox)

        Preview_select_Layout.addStretch()
        Preview_select_Layout.addWidget(self.wellButtonBox)
        Preview_select_Layout.addStretch()

        self.CurrentStepGBox_Layout.addLayout(Parameter_Layout)
        self.CurrentStepGBox_Layout.addLayout(Preview_select_Layout)

        self.CurrentStepGBox.setLayout(self.CurrentStepGBox_Layout)

    def createProgrammBox(self):
        self.ProgrammGBox = QGroupBox("Programm")
        ProgrammBox_layout = QVBoxLayout()

        self.addProgram_Button = QPushButton('Add Step', self)
        self.addProgram_Button.clicked.connect(self.addStep)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget = QWidget()
        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.scrollAreaWidgetLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollArea.setMinimumWidth(400)
        self.addStepBox()
        self.changeStep(1)

        ProgrammBox_layout.addWidget(self.addProgram_Button)
        ProgrammBox_layout.addWidget(self.scrollArea)
        
        self.ProgrammGBox.setLayout(ProgrammBox_layout)

    def addStepBox(self, newStep = True):
        step_nr = self.amount_of_steps
        #StepBox Dict: step_nr: step_nr(0), GroupBox(1), EditButton(2), Delete Button(3), Hour spinBox(4), Min spinBox(5), Sec SpinBox(6)
        self.StepGBoxes[step_nr] = [step_nr,
          QGroupBox('Step ' + str(self.amount_of_steps), self.scrollAreaWidget),
          QPushButton('Edit', self), 
          QPushButton('Delete', self),
          QSpinBox(), QSpinBox(), QSpinBox(),
          QPushButton('', self), 
          QPushButton('', self)]
        
        self.StepGBoxes[step_nr][2].clicked.connect(lambda ignore: self.changeStep(self.StepGBoxes[step_nr][0]))
        self.StepGBoxes[step_nr][3].clicked.connect(lambda ignore: self.deleteStep(self.StepGBoxes[step_nr][0]))

        self.StepGBoxes[step_nr][7].setStyleSheet('border: 0px solid black')
        self.StepGBoxes[step_nr][7].setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-up.svg')))
        self.StepGBoxes[step_nr][8].setStyleSheet('border: 0px solid black')
        self.StepGBoxes[step_nr][8].setIcon(QIcon(os.path.join(basedir, 'resources', 'arrow-down.svg')))

        self.StepGBoxes[step_nr][7].clicked.connect(lambda ignore: self.moveStepUp(self.StepGBoxes[step_nr][0]))
        self.StepGBoxes[step_nr][8].clicked.connect(lambda ignore: self.moveStepDown(self.StepGBoxes[step_nr][0]))

        self.StepGBoxes[step_nr][4].setSuffix(' h')
        self.StepGBoxes[step_nr][4].valueChanged.connect(lambda ignore: self.updateDuration_info(self.StepGBoxes[step_nr][0]))
        self.StepGBoxes[step_nr][5].setSuffix(' min')
        self.StepGBoxes[step_nr][5].setMaximum(59)
        self.StepGBoxes[step_nr][5].setValue(10)
        self.StepGBoxes[step_nr][5].valueChanged.connect(lambda ignore: self.updateDuration_info(self.StepGBoxes[step_nr][0]))
        self.StepGBoxes[step_nr][6].setSuffix(' sec')
        self.StepGBoxes[step_nr][6].setMaximum(59)
        self.StepGBoxes[step_nr][6].valueChanged.connect(lambda ignore: self.updateDuration_info(self.StepGBoxes[step_nr][0]))

        StepGBox_Layout = QGridLayout(self.StepGBoxes[step_nr][1])      
        StepGBox_Layout.addWidget(QLabel('Set duration'), 0, 1, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][4], 0, 2, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][5], 0, 3, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][6], 0, 4, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][2], 1, 3, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][3], 1, 4, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][7], 0, 0, 1, 1)
        StepGBox_Layout.addWidget(self.StepGBoxes[step_nr][8], 1, 0, 1, 1)

        count = self.scrollAreaWidgetLayout.count() - 1
        self.scrollAreaWidgetLayout.insertWidget(count, self.StepGBoxes[step_nr][1])

        if newStep:
            self.StepInformations[step_nr] = [[self.StepGBoxes[step_nr][4].value(), self.StepGBoxes[step_nr][5].value(), self.StepGBoxes[step_nr][6].value()],\
             {'Plate 1 Wells': {}, 'Plate 1 Type':  self.plate_nr_type[0], 'Plate 2 Wells': {}, 'Plate 2 Type': self.plate_nr_type[1]}]

    #Actions and Menus
    def createActions(self):
        self.wellInformationAction = QAction('Informations', self)
        self.wellInformationAction.triggered.connect(self.showWellInformations)
        self.wellSettingsAction = QAction('Get Settings', self)
        self.wellSettingsAction.triggered.connect(self.getWellSettings)     

    def createContextMenu(self):
        self.wellMenu = QMenu(self)
        self.wellMenu.addAction(self.wellInformationAction)
        self.wellMenu.addAction(self.wellSettingsAction)
    
    def showWellContextMenu(self, button_nr, point):
        button = 'Button_' + str(button_nr)
        self.rightClickButtonNr = button_nr
        self.wellMenu.exec_(self.well_buttons[button].mapToGlobal(point))

    # Functions
    def moveStepUp(self, step_nr):
        if step_nr > 1:
            selectedStep = self.StepInformations[step_nr].copy()
            topStep = self.StepInformations[step_nr - 1].copy()

            self.StepInformations[step_nr] = topStep
            self.StepInformations[step_nr - 1] = selectedStep

            topH = topStep[0][0]
            topM = topStep[0][1]
            topS = topStep[0][2]

            selH = selectedStep[0][0]
            selM = selectedStep[0][1]
            selS = selectedStep[0][2]

            self.StepGBoxes[step_nr][4].setValue(topH)
            self.StepGBoxes[step_nr][5].setValue(topM)
            self.StepGBoxes[step_nr][6].setValue(topS)

            self.StepGBoxes[step_nr - 1][4].setValue(selH)
            self.StepGBoxes[step_nr - 1][5].setValue(selM)
            self.StepGBoxes[step_nr - 1][6].setValue(selS)

            self.changeStep(step_nr - 1, modify_Step = True)
            
    def moveStepDown(self, step_nr):
        if step_nr < self.amount_of_steps:
            selectedStep = self.StepInformations[step_nr].copy()
            lowStep = self.StepInformations[step_nr + 1].copy()

            self.StepInformations[step_nr] = lowStep
            self.StepInformations[step_nr + 1] = selectedStep

            lowH = lowStep[0][0]
            lowM = lowStep[0][1]
            lowS = lowStep[0][2]

            selH = selectedStep[0][0]
            selM = selectedStep[0][1]
            selS = selectedStep[0][2]

            self.StepGBoxes[step_nr][4].setValue(lowH)
            self.StepGBoxes[step_nr][5].setValue(lowM)
            self.StepGBoxes[step_nr][6].setValue(lowS)

            self.StepGBoxes[step_nr + 1][4].setValue(selH)
            self.StepGBoxes[step_nr + 1][5].setValue(selM)
            self.StepGBoxes[step_nr + 1][6].setValue(selS)

            self.changeStep(step_nr + 1, modify_Step = True)

    def getWellSettings(self, button_nr = None):
        if button_nr is None:
            well = 'Button_' + str(self.rightClickButtonNr)
        else:
            well = 'Button_' + str(button_nr)
        wellinfo = {}  
        if self.plate_nr == 0:
            try:
                wellinfo = self.StepInformations[self.selceted_step][1]['Plate 1 Wells'][well]
            except:
                wellinfo = None
        elif self.plate_nr == 1:
            try:
                wellinfo = self.StepInformations[self.selceted_step][1]['Plate 2 Wells'][well]
            except:
                wellinfo = None

        if wellinfo is not None:
            self.color = wellinfo['color']
            self.color_chooser.setCurrentText(self.color)
            wvType = wellinfo['waveType']

            if wvType == 'const':
                self.waveTypeCB.setCurrentIndex(0)
            elif wvType == 'sin':
                self.waveTypeCB.setCurrentIndex(1)
            elif wvType == 'tri':
                self.waveTypeCB.setCurrentIndex(2)
            elif wvType == 'sq':
                self.waveTypeCB.setCurrentIndex(3)
            elif wvType == 'pwm':
                self.waveTypeCB.setCurrentIndex(4)
            elif wvType == 'rise':
                self.waveTypeCB.setCurrentIndex(5)
            elif wvType == 'fall':
                self.waveTypeCB.setCurrentIndex(6)

            self.wvMax = wellinfo['maxVal']
            self.maxIntensitySB.setValue(self.wvMax)
            self.maxIntensitySlider.setValue(self.wvMax)

            if wvType not in {'pwm', 'const'}:
                self.wvMin = wellinfo['minVal']
                self.minIntensitySB.setValue(self.wvMin)
                if wvType not in {'rise', 'fall'}:
                    self.wvLen = wellinfo['wvLen']
                    self.wavelengthSB.setValue(self.wvLen)
            elif wvType != 'const':
                self.periodPWM = wellinfo['periodPWM']
                self.periodPWMSB.setValue(self.periodPWM)
                self.dutyCyclePWM = wellinfo['dutyCyclePWM']
                self.dutyCycleSB.setValue(int(self.dutyCyclePWM * 100))
            if wvType not in {'rise', 'fall', 'const'}:
                self.wvStart = wellinfo['start']
                self.startAnimationCB.setCurrentText(self.wvStart)

    def showWellInformations(self):
        self.wellInfoWin = wellInfoWindow(buttonNr = self.rightClickButtonNr, plateNr = self.plate_nr, plateInfo = self.StepInformations, framerate = self.framerate)
        self.wellInfoWin.closed.connect(self.closeInfo)
        self.wellInfoWin.show()
    def closeInfo(self):
        self.wellInfoWin = None

    def changeWavetype(self):
        for row in range(self.ParameterFormlayout.rowCount() - 2):
            self.ParameterFormlayout.removeRow(2)

        self.color = self.color_chooser.currentText()

        self.maxIntensitySB = QSpinBox()
        self.maxIntensitySB.setMaximum(255)
        self.maxIntensitySB.setMinimum(0)
        self.maxIntensitySB.setValue(self.wvMax)
        self.minIntensitySB = QSpinBox()
        self.minIntensitySB.setMaximum(254)
        self.minIntensitySB.setValue(self.wvMin)

        self.maxIntensitySlider = QSlider(Qt.Horizontal)
        self.maxIntensitySlider.setMaximum(255)
        self.maxIntensitySlider.setValue(self.wvMax)

        self.maxIntensitySB.valueChanged.connect(lambda ignore: self.maxIntensitySlider.setValue(self.maxIntensitySB.value()))
        self.maxIntensitySB.valueChanged.connect(lambda ignore: self.minIntensitySB.setMaximum(self.maxIntensitySB.value() - 1))
        self.maxIntensitySB.valueChanged.connect(self.updatePlot)
        self.minIntensitySB.valueChanged.connect(lambda ignore: self.maxIntensitySB.setMinimum(self.minIntensitySB.value() + 1))
        self.minIntensitySB.valueChanged.connect(self.updatePlot)

        self.maxIntensitySlider.valueChanged.connect(lambda ignore: self.maxIntensitySB.setValue(self.maxIntensitySlider.value()))
        self.maxIntensitySlider.valueChanged.connect(self.updatePlot)

        self.wavelengthSB = QSpinBox()
        self.wavelengthSB.setSuffix(' min')
        self.wavelengthSB.setMinimum(1)
        self.wavelengthSB.setValue(self.wvLen)
        self.wavelengthSB.valueChanged.connect(lambda ignore: self.updatePlot())

        self.startAnimationCB = QComboBox()
        self.startAnimationCB.addItem('High')
        self.startAnimationCB.addItem('Low')
        self.startAnimationCB.setCurrentText(self.wvStart)
        self.startAnimationCB.currentIndexChanged.connect(lambda ignore: self.updatePlot())

        self.dutyCycleSB = QSpinBox()
        self.dutyCycleSB.setSuffix(' %')
        self.dutyCycleSB.setMinimum(0)
        self.dutyCycleSB.setMaximum(100)
        self.dutyCycleSB.setValue(int(self.dutyCyclePWM * 100))
        self.dutyCycleSB.valueChanged.connect(lambda ignore: self.updatePlot())

        self.periodPWMSB = QSpinBox()
        self.periodPWMSB.setSuffix(' min')
        self.periodPWMSB.setMinimum(1)
        self.periodPWMSB.setValue(self.periodPWM)
        self.periodPWMSB.valueChanged.connect(lambda ignore: self.updatePlot())

        if self.color_chooser.currentIndex() == 0:
            self.waveTypeCB.setDisabled(True)
        else:
            self.pen = pg.mkPen(color=self.color_chooser.currentText().lower(), width=2)
            self.waveTypeCB.setDisabled(False)
            if self.waveTypeCB.currentIndex() in {1, 2, 3, 5, 6}:
                self.ParameterFormlayout.addRow(QLabel('Max. Intensity: '), self.maxIntensitySB)
            elif self.waveTypeCB.currentIndex() in {0, 4}:
                maxIntensityLayout = QHBoxLayout()
                maxIntensityLayout.addWidget(self.maxIntensitySlider)
                maxIntensityLayout.addWidget(self.maxIntensitySB)
                self.ParameterFormlayout.addRow(QLabel('Intensity: '), maxIntensityLayout)
            if self.waveTypeCB.currentIndex() in {1, 2, 3, 5, 6}:
                self.ParameterFormlayout.addRow(QLabel('Mix. Intensity: '), self.minIntensitySB)
            if self.waveTypeCB.currentIndex() in {1, 2, 3}:
                self.ParameterFormlayout.addRow(QLabel('Wavelength: '), self.wavelengthSB)
            if self.waveTypeCB.currentIndex() == 4:
                self.ParameterFormlayout.addRow(QLabel('Off time: '), self.dutyCycleSB)
            if self.waveTypeCB.currentIndex() == 4:
                self.ParameterFormlayout.addRow(QLabel('Period: '), self.periodPWMSB)
            if self.waveTypeCB.currentIndex() in {1, 2, 3, 4}:
                self.ParameterFormlayout.addRow(QLabel('Starting Intensity: '), self.startAnimationCB)
            
        self.showPlotCB = QCheckBox()
        self.showPlotCB.stateChanged.connect(self.showPlot)

        self.applyChangesButton = QPushButton('Apply', self)
        self.applyChangesButton.clicked.connect(self.applyParameterChanges)
        self.applyChangesButton.setDefault(True)

        self.ParameterFormlayout.addRow(QLabel('Show preview'), self.showPlotCB)
        self.ParameterFormlayout.addRow(QLabel(), self.applyChangesButton)

        if self.getSettingsRB.isChecked():
            self.applyChangesButton.setDisabled(True)
        if self.plotPreviewDisplayed:
            self.showPlotCB.setChecked(True)

        self.updatePlot()

    def updatePlot(self):
        self.wvMax = self.maxIntensitySB.value()
        self.wvMin = self.minIntensitySB.value()
        self.wvStart = self.startAnimationCB.currentText()
        self.wvLen = self.wavelengthSB.value()
        self.dutyCyclePWM = (self.dutyCycleSB.value() / 100)
        self.periodPWM = self.periodPWMSB.value()

        try:
            stepLength = self.StepInformations[self.selceted_step][0][0] * 60 + \
             self.StepInformations[self.selceted_step][0][1] + self.StepInformations[self.selceted_step][0][2] / 60 + self.framerate
        except:
            stepLength = 10

        dp_x = []
        dp_y = []

        if self.color_chooser.currentIndex() == 0:
            self.graphWidget.removeItem(self.data_line)
        else:
            # Const
            if self.waveTypeCB.currentIndex() == 0:
                dp_x = [0, stepLength - self.framerate]
                dp_y = [self.wvMax, self.wvMax]

            # Sine
            elif self.waveTypeCB.currentIndex() == 1:
                a = (self.wvMax - self.wvMin) / 2
                b = 2 * np.pi / self.wvLen
                d = a + self.wvMin
                if self.wvStart == 'Low':
                    c = - (self.wvLen/4)
                elif self.wvStart == 'High':
                    c = (self.wvLen/4)

                time = np.arange(0, stepLength, self.framerate)    
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
            elif self.waveTypeCB.currentIndex() == 2:
                a = (self.wvMax - self.wvMin) / 2
                d = a + self.wvMin
                if self.wvStart == 'Low':
                    c = - (self.wvLen/4)
                elif self.wvStart == 'High':
                    c = (self.wvLen/4)

                time = np.arange(0, stepLength, self.framerate)    
                wave = (4 * a/self.wvLen * abs(((time + c - self.wvLen/4) % self.wvLen) - self.wvLen/2) - a) + d

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
            elif self.waveTypeCB.currentIndex() in {3, 4}:

                TimePeriod = self.periodPWM
                percent = self.dutyCyclePWM
                if self.waveTypeCB.currentIndex() == 3:
                    TimePeriod = self.wvLen
                    percent = 0.5

                time = np.arange(0, stepLength, self.framerate)
                wave = []

                if self.wvStart == 'Low':
                    pwm = time % TimePeriod < TimePeriod * percent
                    for dp in pwm:
                        if dp:
                            wave.append(0)
                        else:
                            wave.append(self.wvMax)
                elif self.wvStart == 'High':
                    pwm = time % TimePeriod < TimePeriod * percent
                    for dp in pwm:
                        if dp:
                            wave.append(self.wvMax)
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
            elif self.waveTypeCB.currentIndex() == 5:
                time = np.arange(0, stepLength, self.framerate)
                wave = []

                diff = self.wvMax - self.wvMin
                dp = self.wvMin

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
            elif self.waveTypeCB.currentIndex() == 6:
                time = np.arange(0, stepLength, self.framerate)
                wave = []

                diff = self.wvMax - self.wvMin
                dp = self.wvMax

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
            
            self.graphWidget.setLimits(xMin = 0, xMax = stepLength - self.framerate + (stepLength - self.framerate) * 0.05, yMin = -1, yMax = 256, minXRange = 5, minYRange = 25)
            self.graphWidget.setXRange(0, stepLength - self.framerate + (stepLength - self.framerate) * 0.05)
            self.graphWidget.removeItem(self.data_line)
            self.data_line =  self.graphWidget.plot(dp_x, dp_y, pen=self.pen)

    def showPlot(self, state):
        if (Qt.Checked == state):
            self.graphProgrammStack.setCurrentIndex(1)
            self.plotPreviewDisplayed = True
            self.updatePlot()
        else:
            self.graphProgrammStack.setCurrentIndex(0)
            self.plotPreviewDisplayed = False

    def changeSelectionType(self, seltyp):
        if seltyp == 0:
            self.ParameterBox.setDisabled(False)
            self.GradientBox.setDisabled(True)
            self.applyChangesButton.setDisabled(False)
            self.selected_wells = set()
            self.applyParameterChanges()

        elif seltyp == 2:
            self.ParameterBox.setDisabled(False)
            self.GradientBox.setDisabled(True)
            self.applyChangesButton.setDisabled(True)
            self.selected_wells = set()
            self.applyParameterChanges()

        elif seltyp == 1:
            self.ParameterBox.setDisabled(True)
            self.GradientBox.setDisabled(False)
            self.selected_wells = set()
            self.graphProgrammStack.setCurrentIndex(0)
            self.plotPreviewDisplayed = False
            self.showPlotCB.setChecked(False)

            self.applyParameterChanges()
            self.select_wells(1)

    def updateDuration_info(self, step_nr):
        self.StepInformations[step_nr][0][0] = self.StepGBoxes[step_nr][4].value()
        self.StepInformations[step_nr][0][1] = self.StepGBoxes[step_nr][5].value()
        self.StepInformations[step_nr][0][2] = self.StepGBoxes[step_nr][6].value()

    def updateDuration_SB(self, step_nr):
        self.StepGBoxes[step_nr][4].valueChanged.disconnect()
        self.StepGBoxes[step_nr][5].valueChanged.disconnect()
        self.StepGBoxes[step_nr][6].valueChanged.disconnect()
        self.StepGBoxes[step_nr][4].setValue(self.StepInformations[step_nr][0][0])
        self.StepGBoxes[step_nr][5].setValue(self.StepInformations[step_nr][0][1])
        self.StepGBoxes[step_nr][6].setValue(self.StepInformations[step_nr][0][2])
        self.StepGBoxes[step_nr][4].valueChanged.connect(lambda ignore: self.updateDuration_info(self.StepGBoxes[step_nr][0]))
        self.StepGBoxes[step_nr][5].valueChanged.connect(lambda ignore: self.updateDuration_info(self.StepGBoxes[step_nr][0]))
        self.StepGBoxes[step_nr][6].valueChanged.connect(lambda ignore: self.updateDuration_info(self.StepGBoxes[step_nr][0]))

    def addStep(self):
        self.amount_of_steps += 1
        self.addStepBox()

    def changeStep(self, step_nr, modify_Step = False):
        # Update Step Information
        selctedPlate = self.plate_nr

        if not modify_Step:
            self.StepInformations[self.selceted_step][1] = self.getStepInfo()

        # Change Step
        self.selceted_step = step_nr

        # Change Style
        for step in self.StepGBoxes:
            self.StepGBoxes[step][1].setStyleSheet("") 
        self.StepGBoxes[step_nr][1].setStyleSheet(
                "QGroupBox{background-color: transparent;"
                "border: 1px solid blue;"
                "border-radius: 5px;"
                "margin-top: 1ex;}"
                "QGroupBox:title {subcontrol-position: top left;"
                "padding: -14px 0px 0px 3px; color:blue;}")
        self.CurrentStepGBox.setTitle('Step ' + str(step_nr))

        # Load Info
        self.loadStepInfo(self.StepInformations[self.selceted_step][1])

        if selctedPlate == 0:
            self.plate_chooser_CB.setCurrentIndex(0)
        elif selctedPlate == 1:
            self.plate_chooser_CB.setCurrentIndex(1)

    def deleteStep(self, step_nr):

        if self.amount_of_steps > 1:
            stillcontinue = True
            # Are you sure Message Box
            if self.StepInformations[step_nr][1] != {'Plate 1 Wells': {}, 'Plate 1 Type': 96, 'Plate 2 Wells': {}, 'Plate 2 Type': 96}:
                stillcontinue = False

            if stillcontinue == False:
                clear_plate_MessageBox = QMessageBox()
                clear_plate = clear_plate_MessageBox.question(self,'', "You already modified Step {}. Do you still want to continue?".format(step_nr), clear_plate_MessageBox.Yes | clear_plate_MessageBox.No)
                if clear_plate_MessageBox.Yes:
                    stillcontinue = True
                else:
                    stillcontinue = False

            if stillcontinue:
                # Update Changes
                self.StepInformations[self.selceted_step][1] = self.getStepInfo()

                # Remove Widget
                for step in range(self.amount_of_steps):
                    self.StepGBoxes[step+1][1].deleteLater()
                    del self.StepGBoxes[step+1]
                    
                new_amount_of_steps = self.amount_of_steps - 1
                self.amount_of_steps = 0

                for step in range(new_amount_of_steps):
                    self.amount_of_steps += 1
                    self.addStepBox(newStep = False)

                # Remove Information
                del self.StepInformations[step_nr]

                higher_steps = []
                for step in self.StepInformations:
                    if step_nr < step:
                        higher_steps.append(step)

                for step in higher_steps:
                    self.StepInformations[step-1] = self.StepInformations.pop(step)

                # Update Information
                for step in self.StepInformations:
                    self.updateDuration_SB(step)

                # Change Step if selected Step deleted
                if step_nr == self.selceted_step:
                    if step_nr == self.amount_of_steps + 1:
                        self.changeStep(self.selceted_step - 1, modify_Step = True)
                    else:
                        self.changeStep(self.selceted_step, modify_Step = True)
                elif step_nr < self.selceted_step:
                    self.changeStep(self.selceted_step-1, modify_Step = True)
                else:
                    self.changeStep(self.selceted_step, modify_Step = True)

    def applyParameterChanges(self):
        if self.color_chooser.currentIndex() == 0:
            for selected_well in self.selected_wells:
                if self.plate_nr == 0: 
                    try:
                        del self.used_wells_plate_1[selected_well]
                    except KeyError:
                        pass
                elif self.plate_nr == 1: 
                    try:
                        del self.used_wells_plate_2[selected_well]
                    except KeyError:
                        pass
        else:
            if self.color_chooser.currentIndex() == 1:
                button_color = (int(sqrt(self.maxIntensitySB.value()) * 15.99), 0, 0)
                light_button_color = (255, 102, 102)
            elif self.color_chooser.currentIndex() == 2:
                button_color = (0, int(sqrt(self.maxIntensitySB.value()) * 15.99), 0)
                light_button_color = (102, 255, 102)
            elif self.color_chooser.currentIndex() == 3:
                button_color = (0, 0, int(sqrt(self.maxIntensitySB.value()) * 15.99))
                light_button_color = (153, 204, 255)
            
            for selected_well in self.selected_wells:
                if self.waveTypeCB.currentIndex() == 0:
                        wellInformation= {
                        'waveType': 'const',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'position': None,
                        'button_color': button_color,
                        'Icon': None}
                elif self.waveTypeCB.currentIndex() == 1:
                        wellInformation= {
                        'waveType': 'sin',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'minVal': self.minIntensitySB.value(),
                        'wvLen': self.wavelengthSB.value(),
                        'start': self.startAnimationCB.currentText(),
                        'position': None,
                        'button_color': light_button_color,
                        'Icon': os.path.join(basedir, 'resources', 'animation-sin.svg')}
                elif self.waveTypeCB.currentIndex() == 2:
                        wellInformation= {
                        'waveType': 'tri',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'minVal': self.minIntensitySB.value(),
                        'wvLen': self.wavelengthSB.value(),
                        'start': self.startAnimationCB.currentText(),
                        'position': None,
                        'button_color': light_button_color,
                        'Icon': os.path.join(basedir, 'resources', 'animation-tri.svg')}
                elif self.waveTypeCB.currentIndex() == 3:
                        wellInformation= {
                        'waveType': 'sq',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'minVal': self.minIntensitySB.value(),
                        'wvLen': self.wavelengthSB.value(),
                        'start': self.startAnimationCB.currentText(),
                        'position': None,
                        'button_color': light_button_color,
                        'Icon': os.path.join(basedir, 'resources', 'animation-sq.svg')}
                elif self.waveTypeCB.currentIndex() == 4:
                        wellInformation= {
                        'waveType': 'pwm',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'dutyCyclePWM': self.dutyCycleSB.value() / 100,
                        'periodPWM': self.periodPWMSB.value(),
                        'start': self.startAnimationCB.currentText(),
                        'position': None,
                        'button_color': light_button_color,
                        'Icon': os.path.join(basedir, 'resources', 'animation-blink.svg')}
                elif self.waveTypeCB.currentIndex() == 5:
                        wellInformation= {
                        'waveType': 'rise',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'minVal': self.minIntensitySB.value(),
                        'position': None,
                        'button_color': light_button_color,
                        'Icon': os.path.join(basedir, 'resources', 'animation-rise.svg')}
                elif self.waveTypeCB.currentIndex() == 6:
                        wellInformation= {
                        'waveType': 'fall',
                        'color': self.color_chooser.currentText(),
                        'maxVal': self.maxIntensitySB.value(),
                        'minVal': self.minIntensitySB.value(),
                        'position': None,
                        'button_color': light_button_color,
                        'Icon': os.path.join(basedir, 'resources', 'animation-fall.svg')}


                if self.plate_nr == 0: 
                    wellInformation['position'] = (0,) + self.Button_to_pos[selected_well]
                    self.used_wells_plate_1[selected_well] = wellInformation
                elif self.plate_nr == 1: 
                    wellInformation['position'] = (1,) + self.Button_to_pos[selected_well]
                    self.used_wells_plate_2[selected_well] = wellInformation

        self.selected_wells = set()
        self.StepInformations[self.selceted_step][1] = self.getStepInfo()
        self.changeButtonColor()

    def createGradient(self):

        '''Creating list of RGB values for Gradient'''

        gradient_values = []
        gradient_color_values = []
        upper_level, lower_level = round(self.max_gradient.value()), round(self.min_gradient.value())

        if self.direction_chooser_gradient.currentIndex() in {0, 1}:
            gradient_step = (upper_level - lower_level) / (self.height_gradient.value() - 1)
            gradient_values = [round(lower_level + (gradient_step * x)) for x in range(self.height_gradient.value())]
        else:
            gradient_step = (upper_level - lower_level) / (self.width_gradient.value() - 1)
            gradient_values = [round(lower_level + (gradient_step * x)) for x in range(self.width_gradient.value())]  

        if self.color_chooser_gradient.currentIndex() == 0:
            for i in range(len(gradient_values)):
                gradient_color_values.append((gradient_values[i],0, 0))
        elif self.color_chooser_gradient.currentIndex() == 1:
            for i in range(len(gradient_values)):
                gradient_color_values.append((0, gradient_values[i], 0))
        elif self.color_chooser_gradient.currentIndex() == 2:
            for i in range(len(gradient_values)):
                gradient_color_values.append((0 ,0, gradient_values[i]))

        '''Creating grandient with positions'''

        self.gradientMatrix = []

        if self.direction_chooser_gradient.currentIndex() in {0, 1}:
            for y in range(self.height_gradient.value()):
                y_pos = y + self.PosTL[0]
                for x in range(self.width_gradient.value()):
                    x_pos = x + self.PosTL[1]
                    if self.direction_chooser_gradient.currentIndex() == 0:
                        self.gradientMatrix.append(((y_pos, x_pos) , (gradient_color_values[-(y+1)])))
                    elif self.direction_chooser_gradient.currentIndex() == 1:
                        self.gradientMatrix.append(((y_pos, x_pos) , (gradient_color_values[y])))
        else:
            for y in range(self.height_gradient.value()):
                y_pos = y + self.PosTL[0]
                for x in range(self.width_gradient.value()):
                    x_pos = x + self.PosTL[1]
                    if self.direction_chooser_gradient.currentIndex() == 2:
                        self.gradientMatrix.append(((y_pos, x_pos) , (gradient_color_values[-(x+1)])))
                    elif self.direction_chooser_gradient.currentIndex() == 3:
                        self.gradientMatrix.append(((y_pos, x_pos) , (gradient_color_values[x])))

        ''' Gradient to enlighted wells'''

        if self.plate_nr == 0:
            gradient_wells_plate_1 = {}
            for well in self.gradientMatrix:
                if well[1][0] != 0:
                    button_color = (int(sqrt(well[1][0]) * 15.99), 0, 0)
                elif well[1][1] != 0:
                    button_color = (0, int(sqrt(well[1][1]) * 15.99), 0)
                elif well[1][2] != 0:
                    button_color = (0, 0, int(sqrt(well[1][2]) * 15.99))
                else:
                    button_color = (0, 0, 0)
                gradient_wells_plate_1[self.Pos_to_Button[well[0]]] = {\
                        'waveType': 'const',\
                        'color': self.color_chooser_gradient.currentText(),\
                        'maxVal': max(well[1]),\
                        'position': (0, well[0][0], well[0][1]),
                        'button_color': button_color,
                        'Icon': None}
        elif self.plate_nr == 1:
            gradient_wells_plate_2 = {}
            for well in self.gradientMatrix:
                if well[1][0] != 0:
                    button_color = (int(sqrt(well[1][0]) * 15.99), 0, 0)
                elif well[1][1] != 0:
                    button_color = (0, int(sqrt(well[1][1]) * 15.99), 0)
                elif well[1][2] != 0:
                    button_color = (0, 0, int(sqrt(well[1][2]) * 15.99))
                gradient_wells_plate_2[self.Pos_to_Button[well[0]]] = {\
                        'waveType': 'const',\
                        'color': self.color_chooser_gradient.currentText(),\
                        'maxVal': max(well[1]),\
                        'position': (1, well[0][0], well[0][1]),
                        'button_color': button_color,
                        'Icon': None}

        if (self.plate_nr == 0 and bool(gradient_wells_plate_1.keys() & self.used_wells_plate_1.keys()))\
         or (self.plate_nr == 1 and bool(gradient_wells_plate_2.keys() & self.used_wells_plate_2.keys())):
            clear_plate_MessageBox = QMessageBox()
            clear_plate = clear_plate_MessageBox.question(self,'', "Some wells in the gradient area are already illuminated.  Do you still want to continue?", clear_plate_MessageBox.Yes | clear_plate_MessageBox.No)
            if clear_plate == clear_plate_MessageBox.Yes:
                if self.plate_nr == 0:
                    self.used_wells_plate_1.update(gradient_wells_plate_1)
                elif self.plate_nr == 1:
                    self.used_wells_plate_2.update(gradient_wells_plate_2)
        else:
            if self.plate_nr == 0:
                self.used_wells_plate_1.update(gradient_wells_plate_1)
            elif self.plate_nr == 1:
                self.used_wells_plate_2.update(gradient_wells_plate_2)

        self.selected_wells = set()             
        self.changeButtonColor()

    def select_row(self, row_nr):
        if self.selectWellsRB.isChecked():
            buttons_that_row = set()
            for pos, well in self.Pos_to_Button.items():
                if pos[0] == row_nr - 1:
                    buttons_that_row.add(well)
            if buttons_that_row.issubset(self.selected_wells) or not bool(buttons_that_row & self.selected_wells):
                for well in buttons_that_row:
                    self.select_well(well)
            else:
                for well in buttons_that_row:
                    if well in self.selected_wells:
                        self.selected_wells.remove(well)
                    self.select_well(well)
        else: 
            pass

    def select_col(self, col_nr):
        if self.selectWellsRB.isChecked():
            buttons_that_col = set()
            for pos, well in self.Pos_to_Button.items():
                if pos[1] == col_nr - 1:
                    buttons_that_col.add(well)
            if buttons_that_col.issubset(self.selected_wells) or not bool(buttons_that_col & self.selected_wells):
                for well in buttons_that_col:
                    self.select_well(well)
            else:
                for well in buttons_that_col:
                    if well in self.selected_wells:
                        self.selected_wells.remove(well)
                    self.select_well(well)
        else:
            pass

    def select_all(self):
        if self.selectWellsRB.isChecked():
            if len(self.selected_wells) != self.plate_type and len(self.selected_wells) != 0:
                self.selected_wells = set()
            for i in range(len(self.Button_to_pos)):
                self.select_well(i+1)
        else:
            pass

    def select_wells(self, button_nr):
        if self.selectWellsRB.isChecked():
            self.select_well(button_nr)
        elif self.getSettingsRB.isChecked():
            self.getWellSettings(button_nr = button_nr)
        elif self.createGradientRB.isChecked():
            self.ButtonNrTL = button_nr
            self.PosTL = self.Button_to_pos['Button_{}'.format(button_nr)]
            self.width_gradient.setMaximum(self.plate_width - self.PosTL[1])
            self.height_gradient.setMaximum(self.plate_height - self.PosTL[0])
            if self.PosTL[0] + self.height_gradient.value() <= self.plate_height and\
             self.PosTL[1] + self.width_gradient.value() <= self.plate_width:
                self.selected_wells = set()
                self.applyParameterChanges()
                for y in range(self.height_gradient.value()):
                    for x in range(self.width_gradient.value()):
                        button_to_select = self.Pos_to_Button[(self.PosTL[0]+y, self.PosTL[1]+x)]
                        self.select_well(int(button_to_select.strip('Button_')))

    def select_well(self, button_nr):
        if isinstance(button_nr, str):
            button_to_select = button_nr
        else:
            button_to_select = 'Button_{}'.format(button_nr)

        if button_to_select in self.selected_wells:
            self.selected_wells.remove(button_to_select)
            if self.plate_nr == 0 and button_to_select in self.used_wells_plate_1:
                button_color = self.used_wells_plate_1[button_to_select]['button_color']
                self.well_buttons[button_to_select].\
                 setStyleSheet("border-radius : {radius}; border: 1px solid black;\
                  background-color: rgb({red}, {green}, {blue})".\
                  format(radius = self.well_button_radius, red = button_color[0],\
                  green = button_color[1], blue = button_color[2]))
                self.well_buttons[button_to_select].setIcon(QIcon(self.used_wells_plate_1[button_to_select]['Icon']))

            elif self.plate_nr == 1 and button_to_select in self.used_wells_plate_2:
                button_color = self.used_wells_plate_2[button_to_select]['button_color']
                self.well_buttons[button_to_select].\
                 setStyleSheet("border-radius : {radius}; border: 1px solid black;\
                  background-color: rgb({red}, {green}, {blue})".\
                  format(radius = self.well_button_radius, red = button_color[0],\
                  green = button_color[1], blue = button_color[2]))
                self.well_buttons[button_to_select].setIcon(QIcon(self.used_wells_plate_2[button_to_select]['Icon']))
            else:
                self.well_buttons[button_to_select].setStyleSheet("border-radius : {radius}; border: 1px solid black".\
                 format(radius = self.well_button_radius))
                self.well_buttons[button_to_select].setIcon(QIcon())

        else:
            self.selected_wells.add(button_to_select)
            self.well_buttons[button_to_select].setStyleSheet("border-radius : {radius}; border: 1px solid black; background-color: #f696ff".\
             format(radius = self.well_button_radius))
            self.well_buttons[button_to_select].setIcon(QIcon())

    def changePlate(self):
        if self.plate_chooser_CB.currentIndex() != 2:
            self.plate_nr = self.plate_chooser_CB.currentIndex()
        else:
            self.plate_nr = 0
        self.selected_wells = set()
        self.graphProgrammStack.setCurrentIndex(0)
        self.plotPreviewDisplayed = False
        self.showPlotCB.setChecked(False)

        if self.plate_nr_type[0] != self.plate_nr_type[1]:
            self.plate_type = self.plate_nr_type[self.plate_nr]

            self.reset(self.plate_type, full_step_reset = False)
            self.wellButtonBox.deleteLater()
            self.createwellButtonBox()

            Preview_select_Layout = QVBoxLayout()
            Preview_select_Layout.addStretch()
            Preview_select_Layout.addWidget(self.wellButtonBox)
            Preview_select_Layout.addStretch()

            self.CurrentStepGBox_Layout.addLayout(Preview_select_Layout)

            self.plate_type_CB.blockSignals(True)
            if self.plate_type == 96:
                self.plate_type_CB.setCurrentIndex(0)
            elif self.plate_type == 24:
                self.plate_type_CB.setCurrentIndex(1)
            elif self.plate_type == 6:
                self.plate_type_CB.setCurrentIndex(2)
            self.plate_type_CB.blockSignals(False)
        else:
            self.reset(self.plate_type, full_step_reset = False)

        self.changeButtonColor()

    def changePlateType(self):
        changePlate = None
        plateEmtpy = False
        oldPlateType = self.plate_type
        newPlateType = None

        if self.plate_type_CB.currentIndex() == 0:
            newPlateType = 96
        elif self.plate_type_CB.currentIndex() == 1:
            newPlateType = 24
        elif self.plate_type_CB.currentIndex() == 2:
            newPlateType = 6
        elif self.plate_type_CB.currentIndex() == 3:
            newPlateType = 0

        if oldPlateType == newPlateType:
            return

        self.graphProgrammStack.setCurrentIndex(0)
        self.plotPreviewDisplayed = False
        self.showPlotCB.setChecked(False)

        for step in self.StepInformations:
            if self.plate_nr == 0:
                if self.StepInformations[step][1]['Plate 1 Wells'] == {}:
                    plateEmtpy = True
            elif self.plate_nr == 1:
                if self.StepInformations[step][1]['Plate 2 Wells'] == {}:
                    plateEmtpy = True

        if not plateEmtpy:
            clear_plate_MessageBox = QMessageBox()
            clear_plate = clear_plate_MessageBox.question(self,'', "When you change the plate type,  all wells already created on this Plate are reset.  Do you still want to continue?", clear_plate_MessageBox.Yes | clear_plate_MessageBox.No)
            if clear_plate == clear_plate_MessageBox.Yes:
                changePlate = True
            else: 
                changePlate = False
        else:
            changePlate = True

        if changePlate:
            self.plate_type = newPlateType
            
            for step in self.StepInformations:
                if self.plate_nr == 0:
                    self.StepInformations[step][1]['Plate 1 Wells'] = {}
                    self.StepInformations[step][1]['Plate 1 Type'] = self.plate_type
                if self.plate_nr == 1:
                    self.StepInformations[step][1]['Plate 2 Wells'] = {}
                    self.StepInformations[step][1]['Plate 2 Type'] = self.plate_type

            self.reset(plate_type = self.plate_type, plate_nr = self.plate_nr)
            self.wellButtonBox.deleteLater()
            self.createwellButtonBox()
            Preview_select_Layout = QVBoxLayout()
            Preview_select_Layout.addStretch()
            Preview_select_Layout.addWidget(self.wellButtonBox)
            Preview_select_Layout.addStretch()

            self.CurrentStepGBox_Layout.addLayout(Preview_select_Layout)

            self.plate_nr_type[self.plate_nr] = self.plate_type

        else:
            self.plate_type_CB.blockSignals(True)
            if self.plate_type == 96:
                self.plate_type_CB.setCurrentIndex(0)
            elif self.plate_type == 24:
                self.plate_type_CB.setCurrentIndex(1)
            elif self.plate_type == 6:
                self.plate_type_CB.setCurrentIndex(2)
            self.plate_type_CB.blockSignals(False)

    def duplicate_plate(self):
        clearPlate = False
        if (self.plate_nr == 0 and self.used_wells_plate_2 != {})\
         or (self.plate_nr == 1 and self.used_wells_plate_1 != {}):
            clear_plate_MessageBox = QMessageBox()
            clear_plate = clear_plate_MessageBox.question(self,'', "Colored wells have already been created for plate {}. Do you still want to continue?".format(2 if self.plate_nr == 0 else 1), clear_plate_MessageBox.Yes | clear_plate_MessageBox.No)
            if clear_plate == clear_plate_MessageBox.Yes:
                clearPlate = True
        else:
            clearPlate = True

        if clearPlate:
            if self.plate_nr == 0:
                if self.plate_nr_type[1] != self.plate_nr_type[0]:
                    for step in self.StepInformations:
                        self.StepInformations[step][1]['Plate 2 Wells'] = {}
                        self.StepInformations[step][1]['Plate 2 Type'] = self.plate_nr_type[0]
                tempWellplate = {}
                for well, settings in self.StepInformations[self.selceted_step][1]['Plate 1 Wells'].items():
                    tempSettings = settings.copy()
                    tempSettings['position'] = (1, settings['position'][1], settings['position'][2])
                    tempWellplate[well] = tempSettings
                self.StepInformations[self.selceted_step][1]['Plate 2 Wells'] = tempWellplate.copy()
                self.used_wells_plate_2 = tempWellplate.copy()
                self.plate_nr_type[1] = self.plate_nr_type[0]
            elif self.plate_nr == 1:
                if self.plate_nr_type[1] != self.plate_nr_type[0]:
                    for step in self.StepInformations:
                        self.StepInformations[step][1]['Plate 1 Wells'] = {}
                        self.StepInformations[step][1]['Plate 1 Type'] = self.plate_nr_type[1]
                tempWellplate = {}
                for well, settings in self.StepInformations[self.selceted_step][1]['Plate 2 Wells'].items():
                    tempSettings = settings.copy()
                    tempSettings['position'] = (0, settings['position'][1], settings['position'][2])
                    tempWellplate[well] = tempSettings
                self.StepInformations[self.selceted_step][1]['Plate 1 Wells'] = tempWellplate.copy()
                self.used_wells_plate_1 = tempWellplate.copy()
                self.plate_nr_type[0] = self.plate_nr_type[1]
        else:
            return


    def changeButtonColor(self):
        self.selected_wells = set()
        for button in self.well_buttons:
            self.well_buttons[button].setStyleSheet("border-radius : {radius}; border: 1px solid black;".format(radius = self.well_button_radius))
            self.well_buttons[button].setIcon(QIcon())
        if self.plate_nr == 0:
            for used_well in self.used_wells_plate_1:
                button_color = self.used_wells_plate_1[used_well]['button_color']
                self.well_buttons[used_well].setStyleSheet("border-radius : {radius}; border: 1px solid black; background-color: rgb({red},{green},{blue})".\
                 format(radius = self.well_button_radius, red = button_color[0], green = button_color[1], blue = button_color[2]))
                self.well_buttons[used_well].setIcon(QIcon(self.used_wells_plate_1[used_well]['Icon']))
        elif self.plate_nr == 1:
            for used_well in self.used_wells_plate_2:
                button_color = self.used_wells_plate_2[used_well]['button_color']
                self.well_buttons[used_well].setStyleSheet("border-radius : {radius}; border: 1px solid black; background-color: rgb({red},{green},{blue})".\
                 format(radius = self.well_button_radius, red = button_color[0], green = button_color[1], blue = button_color[2]))
                self.well_buttons[used_well].setIcon(QIcon(self.used_wells_plate_2[used_well]['Icon']))

    #Settings
    def changeShape(self, imageType):
        self.selectWellsRB.setChecked(True)
        self.createGradientRB.setChecked(False)
        self.changeSelectionType(0)
        if imageType == 'wellplate':
            self.plate_chooser_CBView.setRowHidden(2, True)
            self.plate_type_CBView.setRowHidden(3, True)

            self.plate_type_CB.setCurrentIndex(0)
            self.plate_chooser_CB.setCurrentIndex(0)

            self.PlateChooserBox.setDisabled(False)
            self.createGradientRB.setDisabled(False)

            self.reset()

            for step in self.StepInformations:
                self.StepInformations[step][1]['Plate 1 Wells'] = {}
                self.StepInformations[step][1]['Plate 2 Wells'] = {}
                self.StepInformations[step][1]['Plate 1 Type'] = 96
                self.StepInformations[step][1]['Plate 2 Type'] = 96

        if imageType == 'custompattern':

            self.reset()

            for step in self.StepInformations:
                self.StepInformations[step][1]['Plate 1 Wells'] = {}
                self.StepInformations[step][1]['Plate 2 Wells'] = {}
                self.StepInformations[step][1]['Plate 1 Type'] = 96
                self.StepInformations[step][1]['Plate 2 Type'] = 96

            self.plate_chooser_CBView.setRowHidden(2, False)
            self.plate_type_CBView.setRowHidden(3, False)

            self.plate_type_CB.setCurrentIndex(3)
            self.plate_chooser_CB.setCurrentIndex(2)

            self.PlateChooserBox.setDisabled(True)
            self.createGradientRB.setDisabled(True)

    
    '''
    def framerateChanged(self, framerate = None):
        if framerate is not None:
            self.framerate = framerate
    '''

    #Exporting/Reseting
    def reset(self, plate_type = 96, full_step_reset = True, full_reset = False, plate_nr = None):
        self.plate_type = plate_type

        if self.plate_type == 96:
            self.plate_width = 8
            self.plate_height = 12
            self.well_button_size = 30
            self.well_button_radius = 15
        elif self.plate_type == 24:
            self.plate_width = 4
            self.plate_height = 6
            self.well_button_size = 60
            self.well_button_radius = 30
        elif self.plate_type == 6:
            self.plate_width = 2
            self.plate_height = 3
            self.well_button_size = 120
            self.well_button_radius = 60
        elif self.plate_type == 0:
            self.plate_width = 1
            self.plate_height = 1
            self.well_button_size = 250
            self.well_button_radius = 125

        if full_step_reset or full_reset:
            self.selected_wells = set()

            if plate_nr == 0:
                self.used_wells_plate_1 = {}
                self.plate_nr = 0
            elif plate_nr == 1:
                self.used_wells_plate_2 = {}
                self.plate_nr = 1
            else:
                self.used_wells_plate_1 = {}
                self.used_wells_plate_2 = {}
                self.plate_nr_type[0] = 96
                self.plate_nr_type[1] = 96
                self.plate_nr = 0
                self.plate_chooser_CB.setCurrentIndex(0)
                self.plate_type_CB.setCurrentIndex(0)

            if full_reset:
                for step in range(self.amount_of_steps):
                    self.StepGBoxes[step+1][1].deleteLater()
                    del self.StepGBoxes[step+1]
                self.StepGBoxes = {}
                self.StepInformations = {}
                self.amount_of_steps = 1
                self.selceted_step = 1
                self.addStepBox()
                self.changeStep(1)
                self.changeShape('wellplate')

            self.changeButtonColor()
        
        self.width_gradient.blockSignals(True)
        self.height_gradient.blockSignals(True)
        self.selectWellsRB.setChecked(True)
        self.color_chooser.setCurrentIndex(0)
        self.waveTypeCB.setCurrentIndex(0)
        self.width_gradient.setMaximum(self.plate_width)
        self.height_gradient.setMaximum(self.plate_height)
        self.width_gradient.setValue(self.plate_width)
        self.height_gradient.setValue(self.plate_height)
        self.color_chooser_gradient.setCurrentIndex(0)
        self.direction_chooser_gradient.setCurrentIndex(0)
        self.max_gradient.setValue(255)
        self.min_gradient.setValue(0)
        self.width_gradient.blockSignals(False)
        self.height_gradient.blockSignals(False)

    def getStepInfo(self):
        stepInfo = {'Plate 1 Wells': self.used_wells_plate_1, 'Plate 1 Type': self.plate_nr_type[0],\
         'Plate 2 Wells': self.used_wells_plate_2, 'Plate 2 Type': self.plate_nr_type[1]}

        return stepInfo

    def loadStepInfo(self, stepInfo):
        self.reset(plate_type = self.plate_type, plate_nr = self.plate_nr)

        if self.plate_nr == 0:
            self.plate_chooser_CB.setCurrentIndex(0)
        if self.plate_nr == 1:
            self.plate_chooser_CB.setCurrentIndex(1)
        
        if self.plate_nr_type[self.plate_nr] == 96:
            self.plate_type_CB.setCurrentIndex(0)
        if self.plate_nr_type[self.plate_nr] == 24:
            self.plate_type_CB.setCurrentIndex(1)
        if self.plate_nr_type[self.plate_nr] == 6:
            self.plate_type_CB.setCurrentIndex(2)

        self.used_wells_plate_1 = stepInfo['Plate 1 Wells']
        self.used_wells_plate_2 = stepInfo['Plate 2 Wells']
        
        self.changeButtonColor()

    def getPlateInfo(self):

        return self.StepInformations

    def loadPlateInfo(self, plateInfo):
        if not isinstance(plateInfo, dict):
            plateInfo = ast.literal_eval(plateInfo)

        oldtype = self.StepInformations[1][1]['Plate 1 Type']
        #self.reset(full_reset = True, plate_nr = 0)

        while self.amount_of_steps < len(plateInfo):
            self.addStep()

        self.StepInformations = plateInfo

        for step in self.StepInformations:
            self.updateDuration_SB(step)

        self.plate_type = self.StepInformations[1][1]['Plate 1 Type']

        self.plate_nr_type[0] = self.StepInformations[1][1]['Plate 1 Type']
        self.plate_nr_type[1] = self.StepInformations[1][1]['Plate 2 Type']

        self.loadStepInfo(self.StepInformations[self.selceted_step][1])

    #Copy/Paste
    def copy_wells(self):
        selectedWellsInfo = []
        for well in self.selected_wells:
            if self.plate_nr == 0:
                if well in self.used_wells_plate_1.keys():
                    selectedWellsInfo.append(self.used_wells_plate_1[well])
            else:
                if well in self.used_wells_plate_2.keys():
                    selectedWellsInfo.append(self.used_wells_plate_2[well])
        self.clipboard = sorted(selectedWellsInfo, key=lambda pos: (pos['position'][1], pos['position'][2]))
        self.selected_wells = set()
        self.changeButtonColor()

    def cut_wells(self):
        selectedWellsInfo = []
        for well in self.selected_wells:
            if self.plate_nr == 0:
                if well in self.used_wells_plate_1.keys():
                    selectedWellsInfo.append(self.used_wells_plate_1[well])
                    del self.used_wells_plate_1[well]
            else:
                if well in self.used_wells_plate_2.keys():
                    selectedWellsInfo.append(self.used_wells_plate_2[well])
                    del self.used_wells_plate_2[well]
        sortedPositions = sorted(selectedWellsInfo, key=lambda pos: (pos['position'][1], pos['position'][2]))
        self.selected_wells = set()
        self.changeButtonColor()

    def paste_wells(self):
        if len(self.selected_wells) == 1:
            well_to_paste = self.Button_to_pos[next(iter(self.selected_wells))]
            pasted_wells = []
            if self.plate_nr == 0:
                for well in self.clipboard:
                    newpos = (0, well['position'][1]-self.clipboard[0]['position'][1]+well_to_paste[0], well['position'][2]-self.clipboard[0]['position'][2]+ well_to_paste[1])
                    try:
                        self.used_wells_plate_1[self.Pos_to_Button[(newpos[1], newpos[2])]] = well.copy()
                        self.used_wells_plate_1[self.Pos_to_Button[(newpos[1], newpos[2])]]['position'] = newpos
                    except:
                        pass
            else:
                for well in self.clipboard:
                    newpos = (1, well['position'][1]-self.clipboard[0]['position'][1]+well_to_paste[0], well['position'][2]-self.clipboard[0]['position'][2]+ well_to_paste[1])
                    try:
                        self.used_wells_plate_2[self.Pos_to_Button[(newpos[1], newpos[2])]] = well.copy()
                        self.used_wells_plate_2[self.Pos_to_Button[(newpos[1], newpos[2])]]['position'] = newpos
                    except:
                        pass
            self.selected_wells = set()
            self.changeButtonColor()
