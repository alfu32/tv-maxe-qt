import sys
import os
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

from tvmxutils import PLAYERSTATE_STOPPED, PLAYERSTATE_PLAYING
from tvmxutils import PLAYERSTATE_PAUSED, which

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mplayer import Player, CmdPrefix
# Player.cmd_prefix = ''


class MPlayer(QObject):
    stateChanged = pyqtSignal(int)

    def __init__(self, xid, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.mp = Player(args=(
            '-wid', str(int(xid)),
            '-vf', 'eq2',
            '-fixed-vo',
            '-af', 'volume',
            '-volume', '0',
            '-cache', '512'))
        self.url = None
        self.player_state = PLAYERSTATE_STOPPED
        self.check_state = False

    def play(self, url):
        if self.url == url:
            return
        self.url = url
        if not self.check_state:
            self.check_state = True
            threading.Thread(target=self._monitor_state).start()
        self.mp.loadfile(self.url)

    def _monitor_state(self):
        while self.mp.filename is None:
            time.sleep(1)
        self.mp.pause()
        while self.check_state:
            state = PLAYERSTATE_STOPPED
            if self.mp is None:
                state = PLAYERSTATE_STOPPED
            if self.mp.filename is None:
                state = PLAYERSTATE_STOPPED
            if self.mp.paused:
                state = PLAYERSTATE_PAUSED
            if self.mp.filename and not self.mp.paused:
                state = PLAYERSTATE_PLAYING
            if state != self.player_state:
                self.player_state = state
                self.stateChanged.emit(state)
                return
            time.sleep(0.1)
        self.player_state = PLAYERSTATE_STOPPED

    def pause(self):
        if self.mp:
            self.mp.pause()
            if self.player_state == PLAYERSTATE_PAUSED:
                self.player_state = PLAYERSTATE_PLAYING
            else:
                self.player_state = PLAYERSTATE_PAUSED
            self.stateChanged.emit(self.player_state)

    def unpause(self):
        self.pause()

    def stop(self):
        if self.mp:
            self.mp.stop()
            self.stateChanged.emit(PLAYERSTATE_STOPPED)
        self.check_state = False
        self.url = None

    def setVolume(self, value):
        if self.mp:
            self.mp.volume = value

    def setEq(self, b, c, s, h):
        if self.mp:
            self.mp.brightness = b
            self.mp.contrast = c
            self.mp.saturation = s
            self.mp.hue = h

    def setRatio(self, ratio):
        if not self.mp:
            return
        if ratio == 0:
            ratio = 0
        elif ratio == 1:
            ratio = 1
        elif ratio == 2:
            ratio = 1.5
        elif ratio == 3:
            ratio = 1.33
        elif ratio == 4:
            ratio = 1.25
        elif ratio == 5:
            ratio = 1.55
        elif ratio == 64:
            ratio = 1.4
        elif ratio == 7:
            ratio = 1.77
        elif ratio == 8:
            ratio = 1.6
        elif ratio == 9:
            ratio = 2.35
        self.mp.switch_ratio(ratio)

    def state(self):
        # print("state: {0}".format(self.player_state))
        return self.player_state

plugin_class = MPlayer
