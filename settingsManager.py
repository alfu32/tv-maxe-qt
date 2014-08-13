#-*- coding: utf-8 -*-
from PyQt5.QtCore import *

from singleton import singleton
from appdirs import *


@singleton
class SettingsManager(QObject):
    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.settings = QSettings()
        self._createDefaults()

    def _createDefaults(self):
        # init some default values
        self.settings.beginGroup("General")

        if not self.settings.contains("subscriptions"):
            subscriptions = [
                [1, 'http://tv-maxe.org/subscriptions/Romania.db'],
                [1, 'http://tv-maxe.org/subscriptions/International']
            ]

            self.settings.setValue("subscriptions", subscriptions)

    def value(self, key, defaultValue=None):
        return self.settings.value(key, defaultValue)

    def setValue(self, key, value):
        return self.settings.setValue(key, value)
