# coding: utf8

__author__ = 'Vincent'

import json


class DownloadDirectory:
    def __init__(self):
        self.id = None
        self.path = ''

    def to_string(self):
        return 'id: %s | path: %s' % (str(self.id), self.path)

    def to_update_json(self):
        return {
            "directory":
                json.dumps({
                    "id": self.id,
                    "path": self.path})
        }

    def to_insert_json(self):
        return {
            "directory":
                json.dumps({
                    "path": self.path})
        }