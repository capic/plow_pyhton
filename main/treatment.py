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
        self.stop_loop_file_treatment = False

    @staticmethod
    def start_download(download_id):
        log.log('[Treatment](start_download) +++', log.LEVEL_INFO)
        log.log('[Treatment](start_download) | download_id %d' % download_id, log.LEVEL_DEBUG)

        download_to_start = ManageDownload.get_download_to_start(download_id)
        log.log('[Treatment](start_download) | download to start %s' % (download_to_start.to_string()), log.LEVEL_DEBUG)

        ManageDownload.start_download(download_to_start)

    @staticmethod
    def stop_download(download_id):
        log.log('[Treatment](stop_download) +++', log.LEVEL_INFO)
        log.log('[Treatment](stop_download) | download_id %d' % download_id, log.LEVEL_DEBUG)

        download_to_stop = ManageDownload.get_download_by_id(download_id)
        log.log('[Treatment](stop_download) | download to stop %s' % (download_to_stop.to_string()), log.LEVEL_DEBUG)

        ManageDownload.stop_download(download_to_stop)

    @staticmethod
    def start_file_treatment(file_path):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(config.DIRECTORY_WEB_LOG + 'start_file_treatement.log', 'w',
                                           encoding="UTF-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(file_handler)

        log.log('[Treatment](start_file_treatment) +++', log.LEVEL_INFO)
        log.log('[Treatment](start_file_treatment) | file_path %s' % file_path, log.LEVEL_DEBUG)

        log.log('[Treatment](start_file_treatment) | =========> Insert new links or update old in database <=========',
                log.LEVEL_INFO)
        downloads_to_mark_as_finished_in_file = []
        links_to_mark_as_error_in_file = []

        # insert links in database
        file = open(file_path, 'r', encoding='utf-8')
        for line in file:
            if 'http' in line:
                log.log('[Treatment](start_file_treatment) | Line %s contains http' % line, log.LEVEL_DEBUG)
                download = ManageDownload.manage_download.insert_update_download(line, file_path)

                if download is not None:
                    if download.status == Download.STATUS_FINISHED and ManageDownload.MARK_AS_FINISHED not in line:
                        log.log(
                            '[Treatment](start_file_treatment) | Download id %s already finished in database but not marked in file => mark as finished',
                            log.LEVEL_INFO)
                        downloads_to_mark_as_finished_in_file.append(download)
                else:
                    if ManageDownload.MARK_AS_ERROR not in line and ManageDownload.MARK_AS_FINISHED not in line:
                        links_to_mark_as_error_in_file.append(line)

        file.close()

        for download_to_mark_as_finished in downloads_to_mark_as_finished_in_file:
            Treatment.mark_download_finished_in_file(download_to_mark_as_finished)

        for link_to_mark_as_finished in links_to_mark_as_error_in_file:
            Treatment.mark_link_error_in_file(file_path, link_to_mark_as_finished)

        log.log(
            '[Treatment](start_file_treatment) | =========< End insert new links or update old in database >=========',
            log.LEVEL_INFO)

    @staticmethod
    def mark_link_in_file(file_path, to_replace, replace_by):
        log.log('[Treatment](mark_link_in_file) +++', log.LEVEL_INFO)

        if file_path is not None and file_path != '':
            # try:
            log.log('[Treatment](mark_link_in_file) | =========> Open file %s to read <=========' % file_path, log.LEVEL_INFO)
            f = open(file_path, 'r')
            file_data = f.read()
            f.close()
            log.log('[Treatment](mark_link_in_file) | =========> Close file %s <=========' % file_path, log.LEVEL_INFO)

            log.log('[Treatment](mark_link_in_file) | Replace %s by %s' % (to_replace, replace_by), log.LEVEL_DEBUG)
            new_data = file_data.replace(to_replace, replace_by)

            log.log('[Treatment](mark_link_in_file) | =========> Open file %s to write <=========' % file_path, log.LEVEL_INFO)
            f = open(file_path, 'w')
            f.write(new_data)
            f.close()
            log.log('[Treatment](mark_link_in_file) | =========> Close file %s <=========' % file_path, log.LEVEL_INFO)
        else:
            log.log('[Treatment](mark_link_in_file) | Download is none', log.LEVEL_ERROR)

    @staticmethod
    def mark_download_error_in_file(download):
        log.log('[Treatment](mark_download_error_in_file) +++', log.LEVEL_INFO)
        Treatment.mark_link_in_file(download.file_path, download.link,
                                    '# %s \r\n%s %s' % (
                                        download.name, Treatment.MARK_AS_ERROR, download.link))

    @staticmethod
    def mark_download_finished_in_file(download):
        log.log('[Treatment](mark_download_finished_in_file) +++', log.LEVEL_INFO)
        Treatment.mark_link_in_file(download.file_path, download.link,
                                    '# %s \r\n%s %s' % (
                                        download.name, Treatment.MARK_AS_FINISHED, download.link))

    @staticmethod
    def mark_link_error_in_file(file_path, link):
        log.log('[Treatment](mark_link_error_in_file) +++', log.LEVEL_INFO)
        Treatment.mark_link_in_file(file_path, link,
                                    '%s %s' % (Treatment.MARK_AS_ERROR, link))

    @staticmethod
    def reset_link_finished_in_file(download):
        log.log('[Treatment](reset_link_finished_in_file) +++', log.LEVEL_INFO)
        Treatment.mark_link_in_file(download,
                                    '# %s \r\n%s %s' % (download.name, Treatment.MARK_AS_FINISHED, download.link),
                                    download.link)

    @staticmethod
    def move_download(download_id):
        log.log('[Treatment](move_download) +++', log.LEVEL_INFO)
        download = ManageDownload.get_download_by_id(download_id)
        ManageDownload.move_download(download)

    @staticmethod
    def action(object_id, action_id):
        log.log('[Treatment](action) +++', log.LEVEL_INFO)
        action = ManageDownload.get_action_by_id(action_id)

        if action is not None:
            if action.action_type_id == Action.ACTION_MOVE_DOWNLOAD:
                log.log('[Treatment](action) | Action type: move', log.LEVEL_DEBUG)
                ManageDownload.move_file(object_id, action)
            elif action.action_type_id == Action.ACTION_UNRAR_PACKAGE:
                log.log('[Treatment](action) | Action type: unrar', log.LEVEL_DEBUG)
                ManageDownload.unrar(object_id, action)
        else:
            log.log('[Treatment](action) | Action is none', log.LEVEL_ERROR)

    def start_multi_downloads(self, file_path):
        download = ManageDownload.get_download_to_start(None, file_path)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        while not self.stop_loop_file_treatment and download is not None:
            if len(logger.handlers) > 0:
                logger.handlers[0].stream.close()
                logger.removeHandler(logger.handlers[0])

            file_handler = logging.FileHandler(
                config.DIRECTORY_WEB_LOG + 'log_download_id_' + str(download.id) + '.log', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            logger.addHandler(file_handler)

            log.log('[Treatment](start_multi_downloads) | =========> Start new download <=========', log.LEVEL_INFO)
            if config.RESCUE_MODE is False:
                application_configuration = ManageDownload.get_application_configuration_by_id(1)
                config.LOG_BDD = application_configuration.log_debug_activated
            else:
                # si on est en rescue mode on a pas acces a la base donc on considere que le telechargement est active
                application_configuration = ApplicationConfiguration()
                application_configuration.download_activated = True

            if application_configuration.download_activated:
                download = ManageDownload.start_download(download)

                # mark link with # in file
                if download.status == Download.STATUS_FINISHED:
                    if config.RESCUE_MODE is False:
                        download = ManageDownload.get_download_by_id(download.id)

                    Treatment.mark_download_finished_in_file(download)

                    if config.RESCUE_MODE is False:
                        actions_list = ManageDownload.get_actions_by_parameters(download_id=download.id)

                        for action in actions_list:
                            object_id = None
                            if action.download_id is not None:
                                object_id = action.download_id
                            elif action.download_package_id is not None:
                                object_id = action.download_package_id

                            Treatment.action(object_id, action.id)
                else:
                    if download.status == Download.STATUS_ERROR:
                        Treatment.mark_download_error_in_file(download)
                    else:
                        download.status = Download.STATUS_WAITING

                    download.time_left = 0
                    download.average_speed = 0

                    download.logs = 'updated by start_file_treatment method\r\n'
                    ManageDownload.update_download(download)
                log.log('[Treatment](start_multi_downloads) | =========< End download >=========', log.LEVEL_INFO)
                # next download
                download = ManageDownload.get_download_to_start(None, file_path)
            else:
                # on attend 60s avant de retenter un telechargement
                time.sleep(60)

    def stop_multi_downloads(self, file_path):
        log.log('[Treatment](stop_multi_downloads) +++', log.LEVEL_INFO)

        # TODO: stop current download
        self.stop_loop_file_treatment = True

    @staticmethod
    def check_download_alive(download_id):
        log.log('[Treatment](stop_multi_downloads) +++', log.LEVEL_INFO)

        download_to_check = ManageDownload.get_download_by_id(download_id)
        ManageDownload.check_download_alive(download_to_check)

    @staticmethod
    def check_multi_downloads_alive():
        log.log('[Treatment](check_multi_downloads_alive) +++', log.LEVEL_INFO)

        downloads = ManageDownload.get_downloads_in_progress()

        for download_to_check in downloads:
            ManageDownload.check_download_alive(download_to_check)

    @staticmethod
    def reset(download_id, file_to_delete):
        log.log('[Treatment](reset) +++', log.LEVEL_INFO)

        download = ManageDownload.get_download_by_id(download_id)

        if download is not None:
            if file_to_delete:
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)

            Treatment.reset_link_finished_in_file(download)
        else:
            log.log('[Treatment](reset) | Download is None', log.LEVEL_ERROR)

    @staticmethod
    def delete_package_files(package_id):
        log.log('[Treatment](delete_package_files) +++', log.LEVEL_INFO)

        package = ManageDownload.get_package_by_id(package_id)
        list_downloads = ManageDownload.get_downloads_by_package(package)

        for download in list_downloads:
            try:
                download.log = 'deleting file'
                download.status = Download.STATUS_FILE_DELETING
                ManageDownload.update_download(download)
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)
                download.log = 'delete file ok'
                download.status = Download.STATUS_FILE_DELETED
                ManageDownload.update_download(download)
            except OSError:
                download.log = 'delete file error'
                download.status = Download.STATUS_FILE_DELETE_ERROR
                ManageDownload.update_download(download, force_update_log=True)

