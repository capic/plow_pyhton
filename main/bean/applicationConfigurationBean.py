

__author__ = 'Vincent'

import json


class ApplicationConfiguration:
    def __init__(self):
        self.id = None
        self.download_activated = None
        self.log_debug_activated = None

    def to_string(self):
        return 'id: %s | download_activated: %s | log_debug_activated: %s' % (
            str(self.id), str(self.download_activated), str(self.log_debug_activated))
