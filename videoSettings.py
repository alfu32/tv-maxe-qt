from PyQt5.QtCore import *
from PyQt5 import uic

class VideoSettings(QObject):
    eqChanged = pyqtSignal(dict)
    aspectChanged = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.dialog = uic.loadUi('videoSettings.ui')
        self.dialog.sliderBrightness.valueChanged.connect(self.eqAdjust)
        self.dialog.sliderContrast.valueChanged.connect(self.eqAdjust)
        self.dialog.sliderHue.valueChanged.connect(self.eqAdjust)
        self.dialog.sliderSaturation.valueChanged.connect(self.eqAdjust)
        self.dialog.aspectRatioBox.currentIndexChanged.connect(
            self.changeAspectRatio)
        self.dialog.show()

    def eqAdjust(self, value):
        values = {
            "brightness": self.dialog.sliderBrightness.value(),
            "contrast": self.dialog.sliderContrast.value(),
            "hue": self.dialog.sliderHue.value(),
            "saturation": self.dialog.sliderSaturation.value(),
        }
        self.dialog.labelBrightnessValue.setText(
            "{0}".format(values['brightness']))
        self.dialog.labelContrastValue.setText(
            "{0}".format(values['contrast']))
        self.dialog.labelHueValue.setText(
            "{0}".format(values['hue']))
        self.dialog.labelSaturationValue.setText(
            "{0}".format(values['saturation']))

        self.eqChanged.emit(values)

    def changeAspectRatio(self, index):
        self.aspectChanged.emit(self.dialog.aspectRatioBox.currentText())
