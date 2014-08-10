import time
from os.path import isfile, join, splitext
from os import listdir, getcwd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QMenu, QAction, QSizePolicy
from PyQt5.QtGui import QKeySequence

from videoSettings import VideoSettings


class FullScreenPopup(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setObjectName("fullScreenPopup")
        self.setStyleSheet("#fullScreenPopup{background-color: rgb(0, 0, 0);}")

class VideoManager(QObject):
    stateChanged = pyqtSignal(int)

    def __init__(self, videoWindow, *args, **kwargs):
        super(VideoManager, self).__init__(*args, **kwargs)
        self.backends = []
        self.fullScreenPopup = None
        self.videoSettings = None
        self.videoWindow = videoWindow
        self.videoWindowParent = videoWindow.parentWidget()
        self.videoWindow.mouseDoubleClickEvent = self.switchFullscreen
        self.videoWindow.customContextMenuRequested.connect(
            self.showContextMenu)
        self._prepareBackends()

    def _prepareBackends(self):
        path = join(getcwd(), 'players')
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for fname in files:
            if fname.endswith('.py'):
                mname = splitext(fname)[0]  # module name
                if mname == '__init__':
                    continue
                module = __import__('players.{0}'.format(mname), fromlist=[''])
                self.backends.append(module.plugin_class())

        self.mediaPlayer = self.backends[0]
        self.mediaPlayer.stateChanged.connect(self.playerStateChanged)

    def playVideo(self, url):
        self.mediaPlayer.setMedia(url)
        self.mediaPlayer.play(self.videoWindow.winId())

    def pauseVideo(self):
        self.mediaPlayer.pause()

    def unpauseVideo(self):
        self.mediaPlayer.pause()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def playerStateChanged(self, state):
        self.stateChanged.emit(state)

    def showContextMenu(self, pos):
        contextMenu = QMenu(self.videoWindow)

        fullscreenAction = QAction("Fullscreen", self.videoWindow)
        fullscreenAction.setCheckable(True)
        fullscreenAction.setChecked(self.isFullscreen())
        fullscreenAction.toggled.connect(self.setFullscreen)
        fullscreenAction.setShortcut(QKeySequence("Ctrl+F"))
        contextMenu.addAction(fullscreenAction)

        videoSettingsAction = QAction("Video Settings", self.videoWindow)
        videoSettingsAction.triggered.connect(self.showVideoSettings)
        contextMenu.addAction(videoSettingsAction)

        contextMenu.popup(self.videoWindow.mapToGlobal(pos))

    def isFullscreen(self):
        if self.fullScreenPopup:
            return True
        else:
            return False

    def switchFullscreen(self, event=None):
        if self.isFullscreen():
            self.setFullscreen(False)
        else:
            self.setFullscreen(True)

    def setFullscreen(self, fullscreen):
        if fullscreen:
            self.fullScreenPopup = FullScreenPopup()
            layout = QHBoxLayout(self.fullScreenPopup)
            layout.addWidget(self.videoWindow)
            layout.setContentsMargins(0, 0, 0, 0)
            self.fullScreenPopup.setLayout(layout)
            self.fullScreenPopup.showFullScreen()
        else:
            self.fullScreenPopup.hide()
            self.videoWindowParent.layout().addWidget(self.videoWindow)
            self.fullScreenPopup = None

    def showVideoSettings(self):
        if not self.videoSettings:
            self.videoSettings = VideoSettings(self.videoWindow.window())
            self.videoSettings.eqChanged.connect(self.eqChanged)
            self.videoSettings.aspectChanged.connect(self.aspectChanged)

    def setVolume(self, value):
        self.mediaPlayer.setVolume(value)

    def eqChanged(self, values):
        brightness = values['brightness']
        contrast = values['contrast']
        saturation = values['saturation']
        hue = values['hue']
        self.mediaPlayer.setEq(brightness, contrast, saturation, hue)

    def aspectChanged(self, value):
        self.mediaPlayer.setRatio(value)
