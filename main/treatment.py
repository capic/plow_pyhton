#!/usr/bin/env python

__author__ = 'Vincent'

import logging

from bean.downloadBean import Download
from main.manage_download import ManageDownload


class Treatment:
    def __init__(self):
        self.manage_download = ManageDownload()
        self.stop_loop_file_treatment = False

    def start_download(self, download_id):
        logging.debug('*** start_download ***')
        logging.debug('download_id %s' % (str(download_id).encode('UTF-8')))

        download_to_start = self.manage_download.get_download_to_start(download_id)
        logging.debug('download to start %s' % (download_to_start.to_string().encode('UTF-8')))

        self.manage_download.start_download(download_to_start)

    def stop_download(self, download_id):
        logging.debug('*** stop_download ***')
        logging.debug('download_id %s' % (download_id.encode('UTF-8')))

        download_to_stop = self.manage_download.get_download_by_id(download_id)
        logging.debug('download to stop %s' % (download_to_stop.to_string().encode('UTF-8')))

        self.manage_download.stop_download(download_to_stop)

    def start_file_treatment(self, file_path):
        logging.debug('*** start_file_treatment ***')
        logging.debug('file_path %s' % (file_path.encode('UTF-8')))

        logging.debug('=========> Insert new links or update old in database <=========')
        # insert links in database
        file = open(file_path, 'r')
        for line in file:
            if 'http' in line:
                logging.debug('Line %s contains http' % (line.encode('UTF-8')))
                self.manage_download.insert_update_download(line, file_path)
        file.close()
        logging.debug('%s =========< End insert new links or update old in database >=========')

    def mark_link_finished_in_file(self, download):
        logging.debug('*** mark_link_finished_in_file ***')

        if download is not None:
            # try:
            logging.debug('=========> Open file %s to read <=========' % download.file_path)
            f = open(download.file_path, 'r')
            file_data = f.read()
            f.close()
            logging.debug('=========> Close file %s <=========' % download.file_path)

            new_data = file_data.replace(download.link.encode('UTF-8'),
                                         '# %s \r\n%s %s' % (self.manage_download.MARK_AS_FINISHED,
                                                             download.name.encode('UTF-8'),
                                                             download.link.encode('UTF-8')))

            logging.debug('=========> Open file %s to write <=========' % download.file_path)
            f = open(download.file_path, 'w')
            f.write(new_data)
            f.close()
            logging.debug('=========> Close file %s <=========' % download.file_path)
            # except:
            # logging.error('Unexpected error:', sys.exc_info()[0])
        else:
            logging.error('Download is none')

    def start_multi_downloads(self, file_path):
        logging.debug('*** start_file_treatment ***')
        logging.debug('file_path %s' % (file_path.encode('UTF-8')))

        download = self.manage_download.get_download_to_start(None, file_path)
        while not self.stop_loop_file_treatment and download is not None:
            logging.debug('=========> Start new download <=========')
            download = self.manage_download.start_download(download)

            # mark link with # in file
            if download.status == Download.STATUS_FINISHED:
                self.mark_link_finished_in_file(download)
            else:
                download.status = Download.STATUS_WAITING
                download.time_left = 0
                download.average_speed = 0
                download.infos_plodown = 'updated by start_file_treatment method\r\n'
                self.manage_download.update_download(download)
            logging.debug('=========< End download >=========')
            # next download
            download = self.manage_download.get_download_to_start(None, file_path)

    def stop_multi_downloads(self, file_path):
        logging.debug('*** stop_file_treatment ***')

        # TODO: stop current download
        self.stop_loop_file_treatment = True

    def check_download_alive(self, download_id):
        logging.debug('*** check_download_alive ***')

        download_to_check = self.manage_download.get_download_by_id(download_id)
        self.manage_download.check_download_alive(download_to_check)

    def check_multi_downloads_alive(self):
        logging.debug('*** check_multi_downloads_alive ***')

        downloads = self.manage_download.get_downloads_in_progress(None)

        for download_to_check in downloads:
            self.manage_download.check_download_alive(download_to_check)

    def disconnect(self):
        self.manage_download.disconnect()