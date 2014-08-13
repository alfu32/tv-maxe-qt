from PyQt5.QtCore import *
from PyQt5 import uic
from settingsManager import SettingsManager

SAVE_THIS_CHANNEL_ONLY = 0
SAVE_ALL_CHANNELS = 1


class VideoSettings(QObject):
    eqChanged = pyqtSignal(dict)
    aspectChanged = pyqtSignal(int)
    accepted = pyqtSignal(int)
    canceled = pyqtSignal()
    dismissed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.dialog = uic.loadUi('videoSettings.ui')
        self.dialog.sliderBrightness.valueChanged.connect(self.eqAdjust)
        self.dialog.sliderContrast.valueChanged.connect(self.eqAdjust)
        self.dialog.sliderHue.valueChanged.connect(self.eqAdjust)
        self.dialog.sliderSaturation.valueChanged.connect(self.eqAdjust)
        self.dialog.aspectRatioBox.currentIndexChanged.connect(
            self.changeAspectRatio)
        self.dialog.cancelBtn.clicked.connect(self.cancel)
        self.dialog.saveAllBtn.clicked.connect(self.saveAll)
        self.dialog.saveBtn.clicked.connect(self.saveThis)
        self.dialog.closeEvent = self.closeEvent
        self.dialog.show()

    def eqAdjust(self, value):
        values = self.getCurrentValues()
        self.dialog.labelBrightnessValue.setText(
            "{0}".format(values['brightness']))
        self.dialog.labelContrastValue.setText(
            "{0}".format(values['contrast']))
        self.dialog.labelHueValue.setText(
            "{0}".format(values['hue']))
        self.dialog.labelSaturationValue.setText(
            "{0}".format(values['saturation']))

        self.eqChanged.emit(values)

    def getCurrentValues(self):
        values = {
            "brightness": self.dialog.sliderBrightness.value(),
            "contrast": self.dialog.sliderContrast.value(),
            "hue": self.dialog.sliderHue.value(),
            "saturation": self.dialog.sliderSaturation.value(),
            "aspect": self.dialog.aspectRatioBox.currentIndex()
        }
        return values

    def setValues(self, values):
        self.dialog.sliderBrightness.setValue(int(values['brightness']))
        self.dialog.sliderContrast.setValue(int(values['contrast']))
        self.dialog.sliderSaturation.setValue(int(values['saturation']))
        self.dialog.sliderHue.setValue(int(values['hue']))
        self.dialog.aspectRatioBox.setCurrentIndex(int(values['aspect']))

    def changeAspectRatio(self, index):
        self.aspectChanged.emit(self.dialog.aspectRatioBox.currentIndex())

    def closeEvent(self, event):
        self.dismissed.emit()

    def dismiss(self):
        self.dialog.close()

    def cancel(self):
        self.canceled.emit()

    def saveAll(self):
        self.accepted.emit(SAVE_ALL_CHANNELS)

    def saveThis(self):
        self.accepted.emit(SAVE_THIS_CHANNEL_ONLY)
