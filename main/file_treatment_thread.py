# !/usr/bin/env python

from threading import Thread
from treatment import Treatment
from manage_download import ManageDownload
import log
import sys


class FileTreatmentThread(Thread):
    def __init__(self, file_path):
        Thread.__init__(self)
        self.file_path = file_path

    def run(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Start treatment on %s" % self.file_path, log.LEVEL_DEBUG)
        Treatment.start_file_treatment(self.file_path)

