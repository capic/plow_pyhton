# !/usr/bin/env python

from threading import Thread, Event
from treatment import Treatment
import log
import sys


class DownloadThread(Thread):
    def __init__(self, download, event, dict_event_download_mark_as_finished):
        Thread.__init__(self)
        self.download = download
        self.event = event
        self.dict_event_download_mark_as_finished = dict_event_download_mark_as_finished

    def run(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Start download %s" % self.download.to_string(), log.LEVEL_DEBUG)
        self.dict_event_download_mark_as_finished[self.download.file_path] = Event()
        Treatment.start_download(self.download, self.dict_event_download_mark_as_finished[self.download.file_path])

    def join(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Download %d finished => event setted" % self.download.id,
                log.LEVEL_DEBUG)
        self.event.set()
        del self.dict_event_download_mark_as_finished[download.file_path]


