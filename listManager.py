from PyQt4.QtCore import QUrl, QObject, Qt, QSize
from PyQt4.QtNetwork import QHttp
from PyQt4.QtGui import *
import sqlite3
import json
import base64


class ChannelItem(QListWidgetItem):
    def __init__(self, rowdata):
        super(ChannelItem, self).__init__()
        self.setSizeHint(QSize(16, 28))

        self.url = json.loads(rowdata['streamurls'])
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

    @property
    def widget(self):
        return self._widget


class ListManager(QObject):
    def __init__(self, listWidget):
        super(ListManager, self).__init__(listWidget)
        self.listWidget = listWidget
        self.getList('http://tv-maxe.org/subscriptions/Romania.db')

    def getList(self, listUrl):
        url = QUrl(listUrl)
        self.httpManager = QHttp(self)
        self.httpManager.setHost(url.host())
        self.httpManager.requestFinished.connect(self.listDownloaded)
        self.httpManager.get(url.path())

    def listDownloaded(self):
        if not self.httpManager.hasPendingRequests():
            fh = open('test.db', 'wb')
            fh.write(self.httpManager.readAll())
            fh.close()

            conn = sqlite3.connect('test.db')
            conn.row_factory = sqlite3.Row
            conn.text_factory = str
            data = conn.cursor()

            rows = data.execute("SELECT * FROM tv_channels")
            for row in rows:
                chItem = ChannelItem(row)
                self.listWidget.addItem(chItem)
                self.listWidget.setItemWidget(chItem, chItem.widget)
