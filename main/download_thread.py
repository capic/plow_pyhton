# !/usr/bin/env python

from threading import Thread
from treatment import Treatment
import log
import sys


class DownloadThread(Thread):
    def __init__(self, download, event):
        Thread.__init__(self)
        self.download = download
        self.event = event

    def run(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Start download %s" % self.download.to_string(), log.LEVEL_DEBUG)
        Treatment.start_download(self.download)

    def join(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Download %d finished => event setted" % self.download.id,
                log.LEVEL_DEBUG)
        self.event.set()

