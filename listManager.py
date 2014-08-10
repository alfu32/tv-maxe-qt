from PyQt5.QtCore import QUrl, QObject, Qt, QSize, pyqtSignal
from PyQt5.QtNetwork import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import re
import sqlite3
import json
import base64

import settingsManager
from appdirs import *


class ChannelItem(QListWidgetItem):
    def __init__(self, rowdata):
        super(ChannelItem, self).__init__()
        self.setSizeHint(QSize(16, 28))

        self.urls = json.loads(rowdata['streamurls'])
        self.chid = rowdata['id']
        imgData = base64.b64decode(rowdata['icon'])
        imgPixmap = QPixmap()
        imgPixmap.loadFromData(imgData)

        # UI definition
        self._widget = QWidget()
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(2, 1, 2, 1)

        # channel icon
        self.icon_holder = QLabel()
        self.icon_holder.resize(16, 16)
        self.icon_holder.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Expanding)
        self.icon_holder.setPixmap(imgPixmap)
        self._layout.addWidget(self.icon_holder)

        # channel name label
        self.channeltext = QLabel(rowdata['name'])
        self.channeltext.alignment = Qt.AlignLeft
        self.channeltext.setSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Expanding)
        self._layout.addWidget(self.channeltext)
        self._widget.setLayout(self._layout)

    def __lt__(self, item):
        return self.channeltext.text().lower() < item.channeltext.text().lower()

    @property
    def widget(self):
        return self._widget


class ListManager(QObject):
    listDownloaded = pyqtSignal(str)
    listDownloadFailed = pyqtSignal(str)
    playUrl = pyqtSignal(QUrl)

    def __init__(self, listWidget):
        super(ListManager, self).__init__(listWidget)
        self.listWidget = listWidget
        self.listWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.settingsManager = settingsManager.SettingsManager()

        self.listWidget.itemActivated.connect(self.playCurrentChannel)

    def showContextMenu(self, pos):
        item = self.listWidget.currentItem()
        playAction = QAction("Play", self.listWidget)
        playAction.triggered.connect(self.playCurrentChannel)

        contextMenu = QMenu(self.listWidget)
        contextMenu.addAction(playAction)
        if len(item.urls) > 1:
            submenu = contextMenu.addMenu("Select stream")
            for url in item.urls:
                submenuAction = QAction(url, contextMenu)
                submenuAction.triggered.connect(self.playURL(url))
                submenu.addAction(submenuAction)
        contextMenu.addSeparator()
        contextMenu.addAction(QAction("Channel info", self.listWidget))
        contextMenu.addAction(QAction("Edit channel", self.listWidget))
        contextMenu.addAction(QAction("Remove channel", self.listWidget))
        contextMenu.addSeparator()
        contextMenu.addAction(QAction("TV Guide", self.listWidget))
        contextMenu.popup(self.listWidget.viewport().mapToGlobal(pos))

    def getChannelLists(self):
        for sub in self.settingsManager.subscriptions:
            if sub[0] == 1:
                self.getList(sub[1])

    def getList(self, listUrl):
        url = QUrl(listUrl)
        request = QNetworkRequest(url)
        self.dmanager = QNetworkAccessManager(self)
        self.dmanager.finished.connect(self.listDownloaded)
        self.dmanager.get(request)

    def listDownloaded(self, reply):
        fname = re.sub(r'\W+', '', reply.url().path())
        fname = "{0}/{1}".format(settingsManager.USER_DATA_DIR, fname)

        fh = open(fname, 'wb')
        fh.write(reply.readAll())
        fh.close()

        conn = sqlite3.connect(fname)
        conn.row_factory = sqlite3.Row
        conn.text_factory = str
        data = conn.cursor()

        rows = data.execute("SELECT * FROM tv_channels")
        for row in rows:
            chItem = ChannelItem(row)
            self.listWidget.addItem(chItem)
            self.listWidget.setItemWidget(chItem, chItem.widget)
        self.listWidget.sortItems(Qt.AscendingOrder)

    def playCurrentChannel(self, item=None):
        if not item:
            item = self.listWidget.currentItem()
        self.playUrl.emit(QUrl(item.urls[0]))

    def playURL(self, url):
        def playSelectedURL(checked):
            self.playUrl.emit(QUrl(url))
        return playSelectedURL
