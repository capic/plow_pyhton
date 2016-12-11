# !/usr/bin/env python

from threading import Thread
from treatment import Treatment
import log
import sys
import time
from download_thread import DownloadThread
from manage_download import ManageDownload
from timer import Timer

class DownloadsManagerThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.event = event
        self.download_threads_list = []

    def run(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Start of thread downloads manager", log.LEVEL_DEBUG)

        self.event.clear()
        log.log(__name__, sys._getframe().f_code.co_name, "Start up => check if there are downloads to do", log.LEVEL_DEBUG)

        # a = Timer(10.0, self.event.set(), ["MyTimer"])
        # a.start()

        while True:

            downloads_list = ManageDownload.get_all_downloads_to_start()
            for download in downloads_list:
                log.log(__name__, sys._getframe().f_code.co_name,
                        "Create thread for download id %d" % download.id, log.LEVEL_DEBUG)
                download_thread = DownloadThread(download, self.event)
                download_thread.start()
                self.download_threads_list.append(download_thread)

            # for thread in self.download_threads_list:
            #     thread.join()
            #     log.log(__name__, sys._getframe().f_code.co_name,
            #             "Remove thread for download id %d" % thread.download.id, log.LEVEL_DEBUG)
            #     self.download_threads_list.remove(thread)
            #     log.log(__name__, sys._getframe().f_code.co_name,
            #             "Download finished => event setted", log.LEVEL_DEBUG)
            #     self.event.set()

            log.log(__name__, sys._getframe().f_code.co_name, "Wait for event to start download ....", log.LEVEL_DEBUG)
            self.event.wait()
            self.event.clear()

            log.log(__name__, sys._getframe().f_code.co_name, "Event reveived !!", log.LEVEL_DEBUG)

            time.sleep(1)

    def join(self):
        Thread.join(self)
        log.log(__name__, sys._getframe().f_code.co_name, "End of thread downloads manager", log.LEVEL_DEBUG)
