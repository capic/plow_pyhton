

__author__ = 'Vincent'

import json


class DownloadPackage:

    def __init__(self):
        self.id = None
        self.name = ''
        self.unrar_progress = 0

    def to_string(self):
        return 'id: %s | name: %s | unrar_progress: %s' % (str(self.id), self.name, str(self.unrar_progress))

    def to_update_json(self):
        return {
            "package":
                json.dumps({
                    "id": self.id,
                    "name": self.name,
                    "unrar_progress": self.unrar_progress})
        }

    def to_insert_json(self):
        return {
            "package":
                json.dumps({
                    "name": self.name,
                    "unrar_progress": self.unrar_progress})
        }
