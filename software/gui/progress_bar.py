from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class progressBarWidget(QWidget):
    _close = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(450, 100)

        self.titleLabel = QLabel('Export in progress')
        self.titleLabel.setStyleSheet('font-weight: bold')
        
        self.infoLabel = QLabel("Initialize the export process (this can take a while)...")
        
        self.progress = QProgressBar()
        self.progressLabel = QLabel('0 %')

        self.doneButton = QPushButton('Close Window')
        self.doneButton.setDefault(True)
        self.doneButton.adjustSize()
        self.doneButton.clicked.connect(lambda: self._close.emit(1))

        self.stackBar = QStackedWidget(self)
        self.stackBar.addWidget(self.progress)
        self.stackBar.addWidget(self.doneButton)
        self.stackBar.setCurrentIndex(0)

        mainlay = QVBoxLayout()
        mainlay.addWidget(self.titleLabel)
        mainlay.addWidget(self.infoLabel)

        progresslay = QHBoxLayout()
        progresslay.addWidget(self.stackBar)
        progresslay.addWidget(self.progressLabel)
        mainlay.addLayout(progresslay)

        self.setLayout(mainlay)

    def closeEvent(self, event):
        self._close.emit(0)

