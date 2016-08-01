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
import log
import config


class Treatment:
    def __init__(self):
        self.manage_download = ManageDownload()
        self.stop_loop_file_treatment = False

    def start_download(self, download_id):
        log.log('*** start_download ***', log.LEVEL_INFO)
        log.log('download_id %s' % (str(download_id)), log.LEVEL_DEBUG)

        download_to_start = self.manage_download.get_download_to_start(download_id)
        log.log('download to start %s' % (download_to_start.to_string()), log.LEVEL_DEBUG)

        self.manage_download.start_download(download_to_start)

    def stop_download(self, download_id):
        log.log('*** stop_download ***', log.LEVEL_INFO)
        log.log('download_id %s' % download_id, log.LEVEL_DEBUG)

        download_to_stop = self.manage_download.get_download_by_id(download_id)
        log.log('download to stop %s' % (download_to_stop.to_string()), log.LEVEL_DEBUG)

        self.manage_download.stop_download(download_to_stop)

    def start_file_treatment(self, file_path):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(config.DIRECTORY_WEB_LOG + 'start_file_treatement.log', 'w',
                                           encoding="UTF-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(file_handler)

        log.log('*** start_file_treatment ***', log.LEVEL_INFO)
        log.log('file_path %s' % file_path, log.LEVEL_DEBUG)
        log.log('===> rest address: %s' % config.REST_ADRESSE, log.LEVEL_DEBUG)

        log.log('=========> Insert new links or update old in database <=========', log.LEVEL_INFO)
        downloads_to_mark_as_finished_in_file = []
        links_to_mark_as_error_in_file = []
        # insert links in database
        file = open(file_path, 'r', encoding='utf-8')
        for line in file:
            if 'http' in line:
                log.log('Line %s contains http'.encode("utf-8") % line, log.LEVEL_DEBUG)
                download = self.manage_download.insert_update_download(line, file_path)

                if download is not None:
                    if download.status == Download.STATUS_FINISHED and self.manage_download.MARK_AS_FINISHED not in line:
                        log.log(
                            'Download id %s already finished in database but not marked in file => mark as finished',
                            log.LEVEL_INFO)
                        downloads_to_mark_as_finished_in_file.append(download)
                else:
                    if ManageDownload.MARK_AS_ERROR not in line and ManageDownload.MARK_AS_FINISHED not in line:
                        links_to_mark_as_error_in_file.append(line)

        file.close()

        for download_to_mark_as_finished in downloads_to_mark_as_finished_in_file:
            self.mark_download_finished_in_file(download_to_mark_as_finished)

        for link_to_mark_as_finished in links_to_mark_as_error_in_file:
            self.mark_link_error_in_file(file_path, link_to_mark_as_finished)

        log.log('%s =========< End insert new links or update old in database >=========', log.LEVEL_INFO)

    def mark_link_in_file(self, file_path, to_replace, replace_by):
        log.log('*** mark_link_in_file ***', log.LEVEL_INFO)

        if file_path is not None and file_path != '':
            # try:
            log.log('=========> Open file %s to read <=========' % file_path, log.LEVEL_INFO)
            f = open(file_path, 'r')
            file_data = f.read()
            f.close()
            log.log('=========> Close file %s <=========' % file_path, log.LEVEL_INFO)

            log.log('Replace %s by %s' % (to_replace, replace_by), log.LEVEL_DEBUG)
            new_data = file_data.replace(to_replace, replace_by)

            log.log('=========> Open file %s to write <=========' % file_path, log.LEVEL_INFO)
            f = open(file_path, 'w')
            f.write(new_data)
            f.close()
            log.log('=========> Close file %s <=========' % file_path, log.LEVEL_INFO)
        else:
            logging.error('Download is none')

    def mark_download_error_in_file(self, download):
        log.log('*** mark_download_error_in_file ***', log.LEVEL_INFO)
        self.mark_link_in_file(download.file_path, download.link,
                               '# %s \r\n%s %s' % (download.name, self.manage_download.MARK_AS_ERROR, download.link))

    def mark_download_finished_in_file(self, download):
        log.log('*** mark_download_finished_in_file ***', log.LEVEL_INFO)
        self.mark_link_in_file(download.file_path, download.link,
                               '# %s \r\n%s %s' % (download.name, self.manage_download.MARK_AS_FINISHED, download.link))

    def mark_link_error_in_file(self, file_path, link):
        log.log('*** mark_link_finished_in_file ***', log.LEVEL_INFO)
        self.mark_link_in_file(file_path, link,
                               '%s %s' % (self.manage_download.MARK_AS_ERROR, link))


    def reset_link_finished_in_file(self, download):
        log.log('*** reset_link_finished_in_file ***', log.LEVEL_INFO)
        self.mark_link_in_file(download,
                               '# %s \r\n%s %s' % (download.name, self.manage_download.MARK_AS_FINISHED, download.link),
                               download.link)

    def move_download(self, download_id):
        log.log('*** move_download ***', log.LEVEL_INFO)
        download = self.manage_download.get_download_by_id(download_id)
        self.manage_download.move_download(download)

    def action(self, object_id, action_id):
        log.log('*** action ***', log.LEVEL_INFO)
        action = self.manage_download.get_action_by_id(action_id)

        if action is not None:
            if action.action_type_id == Action.ACTION_MOVE_DOWNLOAD:
                log.log('Action typed: move', log.LEVEL_DEBUG)
                self.manage_download.move_file(object_id, action)
            elif action.action_type_id == Action.ACTION_UNRAR_PACKAGE:
                log.log('Action typed: unrar', log.LEVEL_DEBUG)
                self.manage_download.unrar(object_id, action)
        else:
            log.log('Action is none', log.LEVEL_ERROR)

    def start_multi_downloads(self, file_path):
        download = self.manage_download.get_download_to_start(None, file_path)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        while not self.stop_loop_file_treatment and download is not None:
            if len(logger.handlers) > 0:
                logger.handlers[0].stream.close()
                logger.removeHandler(logger.handlers[0])

            file_handler = logging.FileHandler(
                config.DIRECTORY_WEB_LOG + 'log_download_id_' + str(download.id) + '.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            logger.addHandler(file_handler)

            log.log('=========> Start new download <=========', log.LEVEL_INFO)
            if config.RESCUE_MODE is False:
                application_configuration = self.manage_download.get_application_configuration_by_id(1)
                config.LOG_BDD = application_configuration.log_debug_activated
                log.log(application_configuration.to_string(), log.LEVEL_DEBUG)
            else:
                # si on est en rescue mode on a pas acces a la base donc on considere que le telechargement est active
                application_configuration = ApplicationConfiguration()
                application_configuration.download_activated = True

            if application_configuration.download_activated:
                download = self.manage_download.start_download(download)

                log.log('Download Status %s' % str(download.status), log.LEVEL_DEBUG)
                # mark link with # in file
                if download.status == Download.STATUS_FINISHED:
                    if config.RESCUE_MODE is False:
                        download = self.manage_download.get_download_by_id(download.id)

                    self.mark_download_finished_in_file(download)

                    log.log('download => %s | Directory => %s' % (download.to_string(), download.directory.path),
                            log.LEVEL_DEBUG)
                    if config.RESCUE_MODE is False:
                        actions_list = self.manage_download.get_actions_by_parameters(download_id=download.id)

                        for action in actions_list:
                            object_id = None
                            if action.download_id is not None:
                                object_id = action.download_id
                            elif action.download_package_id is not None:
                                object_id = action.download_package_id

                            self.action(object_id, action.id)
                else:
                    if download.status == Download.STATUS_ERROR:
                        self.mark_download_error_in_file(download)
                    else:
                        download.status = Download.STATUS_WAITING

                    download.time_left = 0
                    download.average_speed = 0

                    download.logs = 'updated by start_file_treatment method\r\n'
                    self.manage_download.update_download(download)
                log.log('=========< End download >=========', log.LEVEL_INFO)
                # next download
                download = self.manage_download.get_download_to_start(None, file_path)
            else:
                # on attend 60s avant de retenter un telechargement
                time.sleep(60)

    def stop_multi_downloads(self, file_path):
        log.log('*** stop_file_treatment ***', log.LEVEL_INFO)

        # TODO: stop current download
        self.stop_loop_file_treatment = True

    def check_download_alive(self, download_id):
        log.log('*** check_download_alive ***', log.LEVEL_INFO)

        download_to_check = self.manage_download.get_download_by_id(download_id)
        self.manage_download.check_download_alive(download_to_check)

    def check_multi_downloads_alive(self):
        log.log('*** check_multi_downloads_alive ***', log.LEVEL_INFO)

        downloads = self.manage_download.get_downloads_in_progress()

        for download_to_check in downloads:
            self.manage_download.check_download_alive(download_to_check)

    def reset(self, download_id, file_to_delete):
        log.log('*** reset ***', log.LEVEL_INFO)

        download = self.manage_download.get_download_by_id(download_id)

        if download is not None:
            if file_to_delete:
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)

            self.reset_link_finished_in_file(download)
        else:
            log.log('Download is None', log.LEVEL_ERROR)

    def delete_package_files(self, package_id):
        log.log('*** delete_package_files ***', log.LEVEL_INFO)

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
