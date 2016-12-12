# !/usr/bin/env python

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from threading import Thread
from treatment import Treatment
from download_file_text_handler import DownloadFileTextHandler
import log
import sys
import time
import config


class FileTreatmentsManagerThread(Thread):
    def __init__(self, event, dict_event_download_mark_as_finished):
        Thread.__init__(self)
        self.event = event
        self.dict_event_download_mark_as_finished = dict_event_download_mark_as_finished

    def run(self):
        log.log(__name__, sys._getframe().f_code.co_name, "Start file treatments manager thread", log.LEVEL_DEBUG)
        event_handler = DownloadFileTextHandler(self.event, self.dict_event_download_mark_as_finished)
        observer = Observer()
        observer.schedule(event_handler, path=config.application_configuration.python_directory_download_text.path,
                          recursive=False)
        observer.start()
        log.log(__name__, sys._getframe().f_code.co_name, "Watching for %s" % config.application_configuration.python_directory_download_text.path, log.LEVEL_DEBUG)

        try:
            while True:
                time.sleep(1)
        except:
            import traceback

            print(traceback.format_exc().splitlines()[-1])
            print("Traceback: %s" % traceback.format_exc())
            observer.stop()
        observer.join()

    def join(self):
        Thread.join(self)
        log.log(__name__, sys._getframe().f_code.co_name, "End of thread file treatments manager", log.LEVEL_DEBUG)
