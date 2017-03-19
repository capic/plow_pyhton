import sys
import config
import log

from threading import Event
from file_treatments_manager_thread import FileTreatmentsManagerThread
from downloads_manager_thread import DownloadsManagerThread


class DownloadsMainManager(object):
    def __init__(self):
        # dictionnaire qui va contenir des evenements pour bloquer le watchdog quand le programme marquera un fichier comme termine
        self.dict_event_download_mark_as_finished = {}
        # Evenement pour declencher la recherche des telechargement a faire
        self.event_check_downloads_to_start = Event()
        self.file_treatments_manager_thread = FileTreatmentsManagerThread(self.event_check_downloads_to_start, self.dict_event_download_mark_as_finished)
        self.downloads_manager_thread = DownloadsManagerThread(self.event_check_downloads_to_start, self.dict_event_download_mark_as_finished)

    def start(self):
        self.file_treatments_manager_thread.start()
        self.downloads_manager_thread.start()

        self.file_treatments_manager_thread.join()
        self.downloads_manager_thread.join()


