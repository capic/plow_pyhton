# coding: utf8
#!/usr/bin/env python

__author__ = 'Vincent'

import utils

from bean.downloadBean import Download
from manage_download import ManageDownload
import logging


class Treatment:
    def __init__(self):
        self.manage_download = ManageDownload()
        self.stop_loop_file_treatment = False

    def start_download(self, download_id):
        utils.log_debug(u'*** start_download ***')
        utils.log_debug(u'download_id %s' % (str(download_id)))

        download_to_start = self.manage_download.get_download_to_start(download_id)
        utils.log_debug(u'download to start %s' % (download_to_start.to_string()))

        self.manage_download.start_download(download_to_start)

    def stop_download(self, download_id):
        utils.log_debug(u'*** stop_download ***')
        utils.log_debug(u'download_id %s' % (download_id))

        download_to_stop = self.manage_download.get_download_by_id(download_id)
        utils.log_debug(u'download to stop %s' % (download_to_stop.to_string()))

        self.manage_download.stop_download(download_to_stop)

    def start_file_treatment(self, file_path):
        utils.log_debug(u'*** start_file_treatment ***')
        utils.log_debug(u'file_path %s' % (file_path))

        utils.log_debug(u'=========> Insert new links or update old in database <=========')
        # insert links in database
        file = open(file_path, 'r')
        for line in file:
            line = line.decode("utf-8")
            if 'http' in line:
                utils.log_debug(u'Line %s contains http' % line)
                self.manage_download.insert_update_download(line, file_path)
        file.close()
        utils.log_debug(u'%s =========< End insert new links or update old in database >=========')

    def mark_link_finished_in_file(self, download):
        utils.log_debug(u'*** mark_link_finished_in_file ***')

        if download is not None:
            # try:
            utils.log_debug(u'=========> Open file %s to read <=========' % download.file_path)
            f = open(download.file_path, 'r')
            file_data = f.read()
            f.close()
            utils.log_debug(u'=========> Close file %s <=========' % download.file_path)

            new_data = file_data.replace(download.link,
                                         '# %s \r\n%s %s' % (download.name,
                                                             self.manage_download.MARK_AS_FINISHED,
                                                             download.link))

            utils.log_debug(u'=========> Open file %s to write <=========' % download.file_path)
            f = open(download.file_path, 'w')
            f.write(new_data)
            f.close()
            utils.log_debug(u'=========> Close file %s <=========' % download.file_path)
            # except:
            # logging.error('Unexpected error:', sys.exc_info()[0])
        else:
            logging.error('Download is none')

    def start_multi_downloads(self, file_path):
        # utils.log_debug(u'*** start_file_treatment ***')
        # utils.log_debug(u'file_path %s' % (file_path))

        download = self.manage_download.get_download_to_start(None, file_path)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        while not self.stop_loop_file_treatment and download is not None:
            if len(logger.handlers) > 0:
                logger.handlers[0].stream.close()
                logger.removeHandler(logger.handlers[0])

            file_handler = logging.FileHandler('/var/www/log/log_download_id_' + str(download.id) + '.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            logger.addHandler(file_handler)

            utils.log_debug(u'=========> Start new download <=========')
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
            utils.log_debug(u'=========< End download >=========')
            # next download
            download = self.manage_download.get_download_to_start(None, file_path)

    def stop_multi_downloads(self, file_path):
        utils.log_debug(u'*** stop_file_treatment ***')

        # TODO: stop current download
        self.stop_loop_file_treatment = True

    def check_download_alive(self, download_id):
        utils.log_debug(u'*** check_download_alive ***')

        download_to_check = self.manage_download.get_download_by_id(download_id)
        self.manage_download.check_download_alive(download_to_check)

    def check_multi_downloads_alive(self):
        utils.log_debug(u'*** check_multi_downloads_alive ***')

        downloads = self.manage_download.get_downloads_in_progress(None)

        for download_to_check in downloads:
            self.manage_download.check_download_alive(download_to_check)

    def disconnect(self):
        self.manage_download.disconnect()