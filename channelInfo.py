from PyQt5.QtCore import *
from PyQt5 import uic


class ChannelInfo(QObject):
    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.dialog = uic.loadUi('channelInfo.ui')
        self.dialog.show()
