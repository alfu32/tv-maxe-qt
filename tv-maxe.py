#!/usr/bin/env python3
import sys
from PyQt4 import QtCore, QtGui, uic

import icons_rc
from listManager import ListManager


class TVMaxe(QtGui.QMainWindow):
    def __init__(self):
        super(TVMaxe, self).__init__()
        self.window = uic.loadUi('mainWindow.ui', self)
        self.window.show()

        self.downloadChannelLists()

    def downloadChannelLists(self):
        listManager = ListManager(self.window.channelListWidget)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    tvmaxe = TVMaxe()
    sys.exit(app.exec_())
