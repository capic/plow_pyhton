# !/usr/bin/env python

from watchdog.events import FileSystemEventHandler
from file_treatment_thread import FileTreatmentThread
import log
import sys

thread_list = []


class DownloadFileTextHandler(FileSystemEventHandler):
    def __init__(self, event, dict_event_download_mark_as_finished):
        self.event = event
        self.dict_event_download_mark_as_finished = dict_event_download_mark_as_finished
        self.thread_list = []

    def on_modified(self, event):
        log.log(__name__, sys._getframe().f_code.co_name, event.src_path, log.LEVEL_DEBUG)

        if event.src_path not in self.dict_event_download_mark_as_finished or not self.dict_event_download_mark_as_finished[event.src_path].is_set():
            log.log(__name__, sys._getframe().f_code.co_name, "File treatment is not blocked", log.LEVEL_DEBUG)
            if event.src_path not in self.thread_list:
                thread = FileTreatmentThread(event.src_path)
                thread.setName(event.src_path)

                log.log(__name__, sys._getframe().f_code.co_name, "Thread added", log.LEVEL_DEBUG)

                self.thread_list.append(thread)
                thread.start()
                thread.join()
                log.log(__name__, sys._getframe().f_code.co_name, "Clear event", log.LEVEL_DEBUG)
                self.event.set()

                log.log(__name__, sys._getframe().f_code.co_name, "Thread finished => remove", log.LEVEL_DEBUG)
                self.thread_list.remove(thread)
            else:
                log.log(__name__, sys._getframe().f_code.co_name, "A thread with same name already exists", log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, "File treatment is blocked => remove blocking", log.LEVEL_DEBUG)
            self.dict_event_download_mark_as_finished[event.src_path].clear()
