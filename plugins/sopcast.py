import random
import subprocess
import threading
import os
from urllib.request import urlopen
from PyQt5.QtCore import QObject, pyqtSignal
from tvmxutils import which


class SopcastPlugin(QObject):
    name = 'SopCast Plugin'
    desc = 'Plugin for playing SopCast streams in TV-Maxe'
    version = '0.01'
    protocols = ['sop']  # supported protocols

    bufferProgress = pyqtSignal(float)
    playReady = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None, config=None):
        super(SopcastPlugin, self).__init__(parent)
        if not config:
            self.config = {}
        self.spc = None
        self._readConfig(config)

    def _readConfig(self, config):
        self.inport = random.randint(10025, 65535)
        self.outport = random.randint(10025, 65535)
        if which('sp-sc-auth'):
            self.spauth = 'sp-sc-auth'
        elif which('sp-sc'):
            self.spauth = 'sp-sc'

    def play(self, url):
        try:
            self.spc = subprocess.Popen(
                [
                    self.spauth,
                    url,
                    str(self.inport),
                    str(self.outport)
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            threading.Thread(target=self.waitConnection).start()
        except Exception as e:
            print(e)
            self.spc = None
            self.error.emit("Cannot start SopCast executable.")

    def waitConnection(self):
        progress = 0.0
        while self.spc:
            line = self.spc.stdout.readline().decode("utf-8")
            if 'nblockAvailable' in line:
                col = line.split()
                try:
                    pr = col[2].split('=')
                    progress = float(pr[1])
                    self.bufferProgress.emit(progress)
                except:
                    pass
                if progress > 60:
                    self.playReady.emit(
                        "http://127.0.0.1:{0}".format(self.outport))
                errorlevel = self.spc.poll()
                if  errorlevel:
                    if errorlevel != -9:
                        self.spc = None
                        self.error.emit("Stream not available.")

    def stop(self):
        if self.spc:
            os.kill(self.spc.pid, 9)
            self.spc = None

plugin_class = SopcastPlugin
