# coding: utf8

__author__ = 'Vincent'

import json


class ApplicationConfiguration:
    def __init__(self):
        self.id = None
        self.log_activated = None

    def to_string(self):
        return 'id: %s | log_activated: %s' % (
            str(self.id), str(self.log_activated))
