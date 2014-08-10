#-*- coding: utf-8 -*-
import configparser
import os
import json

from singleton import singleton
from appdirs import *


USER_DATA_DIR = user_data_dir('TVMaxe', 'ov1d1u')


@singleton
class SettingsManager:
    def __init__(self):
        self.configFile = "{0}/{1}".format(
            USER_DATA_DIR, 'config')
        self.config = configparser.ConfigParser()

        self.createDefaults()
        if not os.path.isdir(USER_DATA_DIR):
            os.mkdir(USER_DATA_DIR)

        if not os.path.exists(self.configFile):
            with open(self.configFile, 'w') as cfh:
                self.config.write(cfh)
        else:
            self.readSettings()

    def createDefaults(self):
        # init some default values
        self.config.add_section('General')

        self.subscriptions = []
        self.subscriptions.append(
            [1, 'http://tv-maxe.org/subscriptions/Romania.db']
        )
        self.subscriptions.append(
            [1, 'http://tv-maxe.org/subscriptions/International']
        )

        self.config.set('General', 'subscriptions',
                        json.dumps(self.subscriptions))

    def readSettings(self):
        self.config.read(self.configFile)
        try:
            self.subscriptions = json.loads(
                self.config.get('General', 'subscriptions')
            )
        except:
            pass
