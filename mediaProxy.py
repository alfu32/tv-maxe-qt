import os
import fcntl
import select
import io
import threading
import subprocess
from queue import Queue
from PyQt5.QtCore import QObject, QUrl, QBuffer, QIODevice, pyqtSignal
from os import listdir, getcwd
from os.path import isfile, join, splitext


class MediaProxy(QObject):
    bufferProgress = pyqtSignal(float)
    playReady = pyqtSignal(str)
    stopVideo = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.current_plugin = None
        self.plugins = []

        path = join(getcwd(), 'plugins')
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for fname in files:
            if fname.endswith('.py'):
                mname = splitext(fname)[0]  # module name
                if mname == '__init__':
                    continue
                module = __import__('plugins.{0}'.format(mname), fromlist=[''])
                self.plugins.append(module.plugin_class())

    def _error(self, message):
        self.stop()
        print("Error: {0}".format(message))
        self.error.emit(message)

    def _readyPlay(self, url):
        self.playReady.emit(url)

    def pluginForUrl(self, url):
        qurl = QUrl(url)
        for plugin in self.plugins:
            if qurl.scheme() in plugin.protocols:
                return plugin
        return None

    def play(self, url):
        self.current_plugin = self.pluginForUrl(url)
        if not self.current_plugin:
            self.error.emit('No plugin found for this URL ({0})'.format(url))
            return

        self.current_plugin.bufferProgress.connect(self.bufferProgress.emit)
        self.current_plugin.playReady.connect(self._readyPlay)
        self.current_plugin.error.connect(self._error)
        threading.Thread(target=self.current_plugin.play, args=(url,)).start()

    def stop(self):
        if self.current_plugin:
            try:
                self.current_plugin.bufferProgress.disconnect()
                self.current_plugin.error.disconnect()
            except:
                pass
            self.current_plugin.stop()
