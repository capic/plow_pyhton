# coding: utf8

__author__ = 'Vincent'

import json


class ApplicationConfiguration:
    def __init__(self):
        self.id = None
        self.download_activated = None

    def to_string(self):
        return 'id: %s | download_activated: %s' % (
            str(self.id), str(self.download_activated))
