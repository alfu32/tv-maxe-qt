from urllib.request import urlopen
from PyQt5.QtCore import QObject, pyqtSignal


class BasePlugin(QObject):
    name = 'Basic Plugin'
    desc = 'Basic TV-Maxe plugin which provides HTTP playback'
    version = '0.01'
    protocols = ['http']  # supported protocols

    bufferProgress = pyqtSignal(float)
    playReady = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None, config=None):
        super(BasePlugin, self).__init__(parent)
        if not config:
            self.config = {}
        self.config = config

    def play(self, url):
        try:
            self.playReady.emit(url)
        except Exception as error:
            self.error.emit(str(error))

    def stop(self):
        pass

plugin_class = BasePlugin
