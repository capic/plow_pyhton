# coding: utf8

__author__ = 'Vincent'

import utils


class DownloadDirectory:

    def __init__(self):
        self.id = None
        self.path = ''

    def to_string(self):
        return 'id: %s | path: %s' % (str(self.id), self.path)

    def to_json(self):
        return {"id": self.id, "path": self.path}

    def to_insert_json(self):
        return {"path": self.path}
