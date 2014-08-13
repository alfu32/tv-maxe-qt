import time
from os.path import isfile, join, splitext
from os import listdir, getcwd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence

import tvmxutils
from videoSettings import *
from settingsManager import SettingsManager


class FullScreenPopup(QWidget):
    popupClosed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setObjectName("fullScreenPopup")
        self.setStyleSheet("#fullScreenPopup{background-color: rgb(0, 0, 0);}")
        shortcut = QShortcut(QKeySequence("Esc"), self, self.close)
        shortcut.activated.connect(self.close)

    def closeEvent(self, event):
        self.popupClosed.emit()

class VideoManager(QObject):
    stateChanged = pyqtSignal(int)

    def __init__(self, videoWindow, *args, **kwargs):
        super(VideoManager, self).__init__(*args, **kwargs)
        self.backends = []
        self.fullScreenPopup = None
        self.videoSettings = None
        self.videoWindow = videoWindow
        self.videoWindowParent = videoWindow.parentWidget()
        self.topWindow = self.videoWindow.window()
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
                self.backends.append(module.plugin_class(
                    self.videoWindow.winId()))

        self.mediaPlayer = self.backends[1]
        print(self.mediaPlayer)
        self.mediaPlayer.stateChanged.connect(self.playerStateChanged)

    def playVideo(self, url):
        self.mediaPlayer.play(url)

    def pauseVideo(self):
        self.mediaPlayer.pause()

    def unpauseVideo(self):
        self.mediaPlayer.pause()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def playerStateChanged(self, state):
        if state == tvmxutils.PLAYERSTATE_PLAYING:
            item = self.topWindow.listManager.lastItem
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
            self.fullScreenPopup.popupClosed.connect(self._restoreVideo)
            layout = QHBoxLayout(self.fullScreenPopup)
            layout.addWidget(self.videoWindow)
            layout.setContentsMargins(0, 0, 0, 0)
            self.fullScreenPopup.setLayout(layout)
            self.fullScreenPopup.showFullScreen()
        else:
            self.fullScreenPopup.close()
            self.fullScreenPopup = None

    def showVideoSettings(self):
        if not self.videoSettings:
            self.videoSettings = VideoSettings(self.topWindow)
            self.videoSettings.eqChanged.connect(self.eqChanged)
            self.videoSettings.aspectChanged.connect(self.aspectChanged)
            self.videoSettings.dismissed.connect(self.videoSettingsClosed)
            self.videoSettings.accepted.connect(self.videoSettingsAccepted)
            self.videoSettings.canceled.connect(self.videoSettingsDismissed)
            lastItem = self.topWindow.listManager.lastItem
            values = self.getGlobalEqValues()
            if lastItem:
                values = self.getEqValuesForChannel(lastItem.chid)
            self.videoSettings.setValues(values)
        else:
            self.videoSettings.dialog.activateWindow()

    def videoSettingsClosed(self):
        self.videoSettings = None

    def videoSettingsDismissed(self):
        values = self.getGlobalEqValues()
        lastItem = self.topWindow.listManager.lastItem
        if lastItem:
            values = self.getEqValuesForChannel(lastItem.chid)
        self.eqChanged(values)
        self.videoSettings.dialog.close()

    def videoSettingsAccepted(self, mode):
        settings = SettingsManager()
        values = self.videoSettings.getCurrentValues()
        if mode == SAVE_THIS_CHANNEL_ONLY:
            channel_settings = settings.value('channel_settings', {})
            lastItem = self.topWindow.listManager.lastItem
            if lastItem:
                channel_settings[lastItem.chid] = values
                settings.setValue('channel_settings', channel_settings)
            else:
                print("Cannot save settings for unknown channel")
        else:
            settings.setValue('video_settings', values)
        self.videoSettings.dialog.close()

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

    def getGlobalEqValues(self):
        settings = SettingsManager()
        return settings.value('video_settings', {
            'brightness': 0,
            'contrast': 0,
            'saturation': 0,
            'hue': 0,
            'aspect': 0
            })

    def getEqValuesForChannel(self, chid):
        settings = SettingsManager()
        if not chid:
            return self.getGlobalEqValues()

        channel_settings = settings.value('channel_settings', {})
        if chid in channel_settings:
            return channel_settings[chid]
        else:
            return self.getGlobalEqValues()

    def _restoreVideo(self):
        self.videoWindowParent.layout().addWidget(self.videoWindow)
