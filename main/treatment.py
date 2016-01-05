# coding: utf8
# !/usr/bin/env python

__author__ = 'Vincent'

import utils

from bean.downloadBean import Download
from manage_download import ManageDownload
import logging
import shutil
import os
import copy


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
        utils.log_debug(u'download_id %s' % download_id)

        download_to_stop = self.manage_download.get_download_by_id(download_id)
        utils.log_debug(u'download to stop %s' % (download_to_stop.to_string()))

        self.manage_download.stop_download(download_to_stop)

    def start_file_treatment(self, file_path):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(utils.DIRECTORY_WEB_LOG + 'start_file_treatement.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(file_handler)

        utils.log_debug(u'*** start_file_treatment ***')
        utils.log_debug(u'file_path %s' % file_path)

        utils.log_debug(u'=========> Insert new links or update old in database <=========')
        downloads_to_mark_as_finished_in_file = []
        # insert links in database
        file = open(file_path, 'r')
        for line in file:
            line = line.decode("utf-8")
            if 'http' in line:
                utils.log_debug(u'Line %s contains http' % line)
                download = self.manage_download.insert_update_download(line, file_path)

                if download is not None and download.status == Download.STATUS_FINISHED and self.manage_download.MARK_AS_FINISHED not in line:
                    utils.log_debug(
                        u'Download id %s already finished in database but not marked in file => mark as finished')
                    downloads_to_mark_as_finished_in_file.append(download)

        file.close()

        for to_mark_as_finished in downloads_to_mark_as_finished_in_file:
            self.mark_link_finished_in_file(to_mark_as_finished)

        utils.log_debug(u'%s =========< End insert new links or update old in database >=========')

    def mark_link_in_file(self, download, to_replace, replace_by):
        utils.log_debug(u'*** mark_link_in_file ***')

        if download is not None:
            # try:
            utils.log_debug(u'=========> Open file %s to read <=========' % download.file_path)
            f = open(download.file_path, 'r')
            file_data = f.read()
            f.close()
            utils.log_debug(u'=========> Close file %s <=========' % download.file_path)

            new_data = file_data.replace(to_replace, replace_by)

            utils.log_debug(u'=========> Open file %s to write <=========' % download.file_path)
            f = open(download.file_path, 'w')
            f.write(new_data)
            f.close()
            utils.log_debug(u'=========> Close file %s <=========' % download.file_path)

            download.logs += 'Text %s replaced by %s in file %s\r\n' % (to_replace, replace_by, download.file_path)
            self.manage_download.update_download_log(download)
            # except:
            # logging.error('Unexpected error:', sys.exc_info()[0])
        else:
            logging.error('Download is none')

    def mark_link_error_in_file(self, download):
        utils.log_debug(u'*** mark_link_error_in_file ***')
        self.mark_link_in_file(download, download.link,
                               '# %s \r\n%s %s' % (download.name, self.manage_download.MARK_AS_ERROR, download.link))

    def mark_link_finished_in_file(self, download):
        utils.log_debug(u'*** mark_link_finished_in_file ***')
        self.mark_link_in_file(download, download.link,
                               '# %s \r\n%s %s' % (download.name, self.manage_download.MARK_AS_FINISHED, download.link))

    def reset_link_finished_in_file(self, download):
        utils.log_debug(u'*** reset_link_finished_in_file ***')
        self.mark_link_in_file(download,
                               '# %s \r\n%s %s' % (download.name, self.manage_download.MARK_AS_FINISHED, download.link),
                               download.link)

    def move_download(self, download_id):
        download = self.manage_download.get_download_by_id(download_id)
        self.manage_download.move_download(download)

    def move_file(self, download_id, src_directory_id, dest_directory_id):
        utils.log_debug(u'*** move_file ***')

        download = self.manage_download.get_download_by_id(download_id)
        src_directory = self.manage_download.get_download_directory_by_id(src_directory_id)
        dest_directory = self.manage_download.get_download_directory_by_id(dest_directory_id)

        if download is not None and src_directory is not None and dest_directory is not None:
            download.status = Download.STATUS_MOVING
            src_file_path = os.path.join(src_directory.path, download.name)

            download.logs = 'Move file in progress, from %s to %s\r\n' % (src_file_path, dest_directory.path)
            self.manage_download.update_download(download)

            if os.path.isfile(src_file_path):
                utils.log_debug(u'downloaded file exists')
                download.logs = 'File %s exists\r\n' % src_file_path
                self.manage_download.update_download_log(download)

                try:
                    utils.log_debug(u'Moving file')
                    shutil.move(src_file_path, dest_directory.path)

                    download.status = Download.STATUS_MOVED
                    download.directory = dest_directory
                    download.to_move_directory = None
                    download.logs = 'Moving to %s OK\r\n' % dest_directory.path
                    self.manage_download.update_download(download)

                    utils.log_debug(u'OK')
                    print("#OK#")
                except IOError as err:
                    download.to_move_directory = None
                    download.status = Download.STATUS_ERROR_MOVING
                    download.logs = 'Error: %s\r\n' % err
                    self.manage_download.update_download(download)

                    utils.log_debug(u"Error: %s" % err)
                    print("#Error: %s#" % err)
            else:
                download.to_move_directory = None
                download.status = Download.STATUS_ERROR_MOVING
                download.logs = 'ERROR: File %s does not exists\r\n' % src_file_path
                self.manage_download.update_download(download)

                utils.log_debug(u"ERROR: File %s does not exists" % src_file_path)
                print("#ERROR: File %s does not exists#" % src_file_path)
        else:
            utils.log_debug(u"ERROR: download or directory are None")
            print("#ERROR: download or directory are None#")

    def move_file2(self, download_id, src_directory_id, dest_directory_id):
        utils.log_debug(u'*** move_file2 ***')

        download = self.manage_download.get_download_by_id(download_id)
        src_directory = self.manage_download.get_download_directory_by_id(src_directory_id)
        dest_directory = self.manage_download.get_download_directory_by_id(dest_directory_id)

        if download is not None and src_directory is not None and dest_directory is not None:
            download.status = Download.STATUS_MOVING
            src_file_path = os.path.join(src_directory.path, download.name)

            download.logs = 'Move file in progress, from %s to %s\r\n' % (src_file_path, dest_directory.path)
            self.manage_download.update_download(download)

            if os.path.isfile(src_file_path):
                utils.log_debug(u'downloaded file exists')
                download.logs = 'File %s exists\r\n' % src_file_path
                self.manage_download.update_download_log(download)

                try:
                    utils.log_debug(u'Moving file')
                    shutil.move(src_file_path, dest_directory.path)

                    download.status = Download.STATUS_MOVED
                    download.directory = dest_directory
                    download.to_move_directory = None
                    download.logs = 'Moving to %s OK\r\n' % dest_directory.path
                    self.manage_download.update_download(download)

                    utils.log_debug(u'OK')
                    print("#OK#")
                except IOError as err:
                    download.to_move_directory = None
                    download.status = Download.STATUS_ERROR_MOVING
                    download.logs = 'Error: %s\r\n' % err
                    self.manage_download.update_download(download)

                    utils.log_debug(u"Error: %s" % err)
                    print("#Error: %s#" % err)
            else:
                download.to_move_directory = None
                download.status = Download.STATUS_ERROR_MOVING
                download.logs = 'ERROR: File %s does not exists\r\n' % src_file_path
                self.manage_download.update_download(download)

                utils.log_debug(u"ERROR: File %s does not exists" % src_file_path)
                print("#ERROR: File %s does not exists#" % src_file_path)
        else:
            utils.log_debug(u"ERROR: download or directory are None")
            print("#ERROR: download or directory are None#")

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

            file_handler = logging.FileHandler(utils.DIRECTORY_WEB_LOG + 'log_download_id_' + str(download.id) + '.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            logger.addHandler(file_handler)

            utils.log_debug(u'=========> Start new download <=========')
            download = self.manage_download.start_download(download)

            utils.log_debug(u'Download Status %s' % str(download.status))
            # mark link with # in file
            if download.status == Download.STATUS_FINISHED:
                if download.id != -1:
                    download = self.manage_download.get_download_by_id(download.id)
                self.mark_link_finished_in_file(download)

                utils.log_debug(u'download => %s | Directory => %s' % (download.to_string(), download.directory.path))
                if download.to_move_directory is not None and download.to_move_directory.id != utils.DIRECTORY_DOWNLOAD_DESTINATION_ID:
                    utils.log_debug(u'File will be moved...............')
                    self.manage_download.move_download(download)
            else:
                if download.status == Download.STATUS_ERROR:
                    self.mark_link_error_in_file(download)
                else:
                    download.status = Download.STATUS_WAITING

                download.time_left = 0
                download.average_speed = 0

                download.logs = 'updated by start_file_treatment method\r\n'
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

        downloads = self.manage_download.get_downloads_in_progress()

        for download_to_check in downloads:
            self.manage_download.check_download_alive(download_to_check)

    def unrar(self, download_id):
        utils.log_debug(u'*** unrar ***')

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(utils.DIRECTORY_WEB_LOG + 'log_unrar_id_' + str(download_id) + '.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(file_handler)

        download = self.manage_download.get_download_by_id(download_id)

        if download is not None:
            filename, file_extension = os.path.splitext(download.name)

            if file_extension == '.rar':
                downloads_list = self.manage_download.get_downloads_by_package(download.package)

                if downloads_list is not None and len(downloads_list) > 0:
                    def getKey(d):
                        return d.name

                    downloads_list = sorted(downloads_list, key=getKey)
                    self.manage_download.unrar(downloads_list)

                else:
                    utils.log_debug(u'No downloads')
            else:
                utils.log_debug(u'download %s is not a rar file' % download.id)

    def reset(self, download_id, file_to_delete):
        utils.log_debug(u'*** reset ***')

        download = self.manage_download.get_download_by_id(download_id)

        if download is not None:
            if file_to_delete:
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)

            self.reset_link_finished_in_file(download)
        else:
            utils.log_debug(u'Download is None')

    def delete_package_files(self, package_id):
        utils.log_debug(u'*** delete_package_files ***')

        package = self.manage_download.get_package_by_id(package_id)
        list_downloads = self.manage_download.get_downloads_by_package(package)

        for download in list_downloads:
            try:
                download.log = 'deleting file'
                download.status = Download.STATUS_FILE_DELETING
                self.manage_download.update_download(download)
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)
                download.log = 'delete file ok'
                download.status = Download.STATUS_FILE_DELETED
                self.manage_download.update_download(download)
            except OSError:
                download.log = 'delete file error'
                download.status = Download.STATUS_FILE_DELETE_ERROR
                self.manage_download.update_download(download)

    def disconnect(self):
        self.manage_download.disconnect()
