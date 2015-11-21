# coding: utf8

__author__ = 'Vincent'


class DownloadHost:

    def __init__(self):
        self.id = None
        self.name = ''

    def to_string(self):
        return 'id: %s | name: %s' % (str(self.id), self.name)

    def to_json(self):
        return {"id": self.id, "name": self.name}

    def to_insert_json(self):
        return {"name": self.name}
