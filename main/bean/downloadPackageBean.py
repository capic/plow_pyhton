# coding: utf8

__author__ = 'Vincent'


class DownloadPackage:

    def __init__(self):
        self.id = None
        self.name = ''
        self.unrar_progress = 0

    def to_string(self):
        return 'id: %s | name: %s | unrar_progress: %s' % (str(self.id), self.name, str(self.unrar_progress))

    def to_json(self):
        return {"id": self.id, "name": self.name, "unrar_progress": self.unrar_progress}

    def to_insert_json(self):
        return {"name": self.name, "unrar_progress": self.unrar_progress}