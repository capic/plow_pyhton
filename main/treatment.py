# coding: utf8
# !/usr/bin/env python

__author__ = 'Vincent'

import utils

from bean.downloadBean import Download
from bean.actionBean import Action
from manage_download import ManageDownload
from bean.applicationConfigurationBean import ApplicationConfiguration
import logging
import shutil
import os
import copy
import time


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
        utils.log_debug('===> rest address: %s' % utils.log_debug(utils.REST_ADRESSE))

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

            utils.log_debug(u'Replace %s by %s' % (to_replace, replace_by))
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

    def action(self, object_id, action_id, action_target_id):
        utils.log_debug(u'*** action ***')
        action = self.manage_download.get_action_by_id(action_id)

        if action is not None:
            if action.action_type_id == Action.ACTION_MOVE_DOWNLOAD:
                utils.log_debug(u'Action typed: move')
                self.manage_download.move_file(object_id, action)
            elif action.action_type_id == Action.ACTION_UNRAR_PACKAGE:
                utils.log_debug(u'Action typed: unrar')
                self.manage_download.unrar(object_id, action)
        else:
            utils.log_debug(u'Action is none')

    def start_multi_downloads(self, file_path):
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
            if utils.RESCUE_MODE is False:
                application_configuration = self.manage_download.get_application_configuration_by_id(1)
                utils.LOG_BDD = application_configuration.log_debug_activated
                utils.log_debug(application_configuration.to_string())
            else:
                # si on est en rescue mode on a pas acces a la base donc on considere que le telechargement est active
                application_configuration = ApplicationConfiguration()
                application_configuration.download_activated = True

            if application_configuration.download_activated:
                download = self.manage_download.start_download(download)

                utils.log_debug(u'Download Status %s' % str(download.status))
                # mark link with # in file
                if download.status == Download.STATUS_FINISHED:
                    if utils.RESCUE_MODE is False:
                        download = self.manage_download.get_download_by_id(download.id)
                    self.mark_link_finished_in_file(download)

                    utils.log_debug(u'download => %s | Directory => %s' % (download.to_string(), download.directory.path))
                    if utils.RESCUE_MODE is False:
                        actions_list = self.manage_download.get_actions_by_parameters(download_id=download.id)

                        for action in actions_list:
                            object_id = None
                            if action.download_id is not None:
                                object_id = action.download_id
                            elif action.download_package_id is not None:
                                object_id = action.download_package_id

                            self.action(object_id, action)
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
            else:
                # on attend 60s avant de retenter un telechargement
                time.sleep(60)

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
                self.manage_download.update_download(download, force_update_log=True)

    def disconnect(self):
        self.manage_download.disconnect()
