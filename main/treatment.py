
# !/usr/bin/env python

__author__ = 'Vincent'

import copy
import logging
import os
import shutil
import sys
import time
import subprocess

import config
import log
import utils
from bean.actionBean import Action
from bean.applicationConfigurationBean import ApplicationConfiguration
from bean.downloadBean import Download

from manage_download import ManageDownload


class Treatment:
    def __init__(self):
        self.stop_loop_file_treatment = False

    @staticmethod
    def start_download(download, event_download_mark_as_finished):
        log.log(__name__, sys._getframe().f_code.co_name, 'download %s' % download.to_string(), log.LEVEL_DEBUG)

        log.init('log_download_id_%d.log', download)
        download = ManageDownload.start_download(download)

        # mark link with # in file
        if download.status == Download.STATUS_FINISHED:
            # change the file permission
            log.log(__name__, sys._getframe().f_code.co_name,
                    "Change file permission %s" % download.directory.path + download.name, log.LEVEL_INFO, True,
                    download)
            os.chmod(download.directory.path + download.name, 0o777)

            if config.RESCUE_MODE is False:
                download = ManageDownload.get_download_by_id(download.id)

            log.log(__name__, sys._getframe().f_code.co_name, "Event to block file changes detection setted", log.LEVEL_INFO)
            event_download_mark_as_finished.set()
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

            log.log(__name__, sys._getframe().f_code.co_name, "Updated by start_file_treatment method", log.LEVEL_DEBUG,
                    True, download)

            # change the file permission
            # log.log(__name__, sys._getframe().f_code.co_name, "Change file permission", log.LEVEL_INFO, True, download)
            # os.chmod(download.directory.path + download.name, 0o777)
        log.log(__name__, sys._getframe().f_code.co_name, '=========< End download >=========', log.LEVEL_INFO)

    @staticmethod
    def stop_download(download_id):
        log.log(__name__, sys._getframe().f_code.co_name, 'download_id %d' % download_id, log.LEVEL_DEBUG)

        download_to_stop = ManageDownload.get_download_by_id(download_id)
        log.log(__name__, sys._getframe().f_code.co_name, 'download to stop %s' % (download_to_stop.to_string()), log.LEVEL_DEBUG)

        ManageDownload.stop_download(download_to_stop)

    @staticmethod
    def start_file_treatment(file_path):
        log.init('start_file_treatement.log')
        # log.init_log_file('start_file_treatement.log', config.application_configuration.python_log_format)

        log.log(__name__, sys._getframe().f_code.co_name, 'file_path %s' % file_path, log.LEVEL_DEBUG)

        log.log(__name__, sys._getframe().f_code.co_name, '=========> Insert new links or update old in database <=========',
                log.LEVEL_INFO)
        downloads_to_mark_as_finished_in_file = []
        links_to_mark_as_error_in_file = []

        # insert links in database
        file = open(file_path, 'r', encoding='utf-8')
        for line in file:
            if 'http' in line:
                log.log(__name__, sys._getframe().f_code.co_name, 'Line %s contains http' % line, log.LEVEL_DEBUG)
                download = ManageDownload.insert_update_download(line, file_path)

                if download is not None:
                    if download.status == Download.STATUS_FINISHED and ManageDownload.MARK_AS_FINISHED not in line:
                        log.log(__name__, sys._getframe().f_code.co_name,
                            'Download id %s already finished in database but not marked in file => mark as finished',
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

        log.log(__name__, sys._getframe().f_code.co_name,
            '=========< End insert new links or update old in database >=========',
            log.LEVEL_INFO)

    @staticmethod
    def mark_link_in_file(file_path, to_replace, replace_by, download=None):
        if file_path is not None and file_path != '':
            # try:
            log.log(__name__, sys._getframe().f_code.co_name, '=========> Open file %s to read <=========' % file_path, log.LEVEL_INFO, True, download)
            f = open(file_path, 'r', encoding='utf-8')
            file_data = f.read()
            f.close()
            log.log(__name__, sys._getframe().f_code.co_name, '=========> Close file %s <=========' % file_path, log.LEVEL_INFO, True, download)

            log.log(__name__, sys._getframe().f_code.co_name, 'Replace %s by %s' % (to_replace, replace_by), log.LEVEL_DEBUG, True, download)
            new_data = file_data.replace(to_replace, replace_by)

            log.log(__name__, sys._getframe().f_code.co_name, '=========> Open file %s to write <=========' % file_path, log.LEVEL_INFO, True, download)
            f = open(file_path, 'w', encoding='utf-8')
            f.write(new_data)
            f.close()
            log.log(__name__, sys._getframe().f_code.co_name, '=========> Close file %s <=========' % file_path, log.LEVEL_INFO, True, download)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Download is none', log.LEVEL_ERROR, True, download)

    @staticmethod
    def mark_download_error_in_file(download):
        Treatment.mark_link_in_file(download.file_path, download.link,
                                    '# %s \r\n%s %s' % (
                                        download.name, ManageDownload.MARK_AS_ERROR, download.link), download)

    @staticmethod
    def mark_download_finished_in_file(download):
        Treatment.mark_link_in_file(download.file_path, download.link,
                                    '# %s \r\n%s %s' % (
                                        download.name, ManageDownload.MARK_AS_FINISHED, download.link), download)

    @staticmethod
    def mark_link_error_in_file(file_path, link):
        Treatment.mark_link_in_file(file_path, link,
                                    '%s %s' % (ManageDownload.MARK_AS_ERROR, link))

    @staticmethod
    def reset_link_finished_in_file(download):
        Treatment.mark_link_in_file(download,
                                    '# %s \r\n%s %s' % (download.name, ManageDownload.MARK_AS_FINISHED, download.link),
                                    download.link, download)

    @staticmethod
    def move_download(download_id):
        download = ManageDownload.get_download_by_id(download_id)
        ManageDownload.move_download(download)

    @staticmethod
    def action(object_id, action_id):
        action = ManageDownload.get_action_by_id(action_id)

        if action is not None:
            if action.action_type_id == Action.ACTION_MOVE_DOWNLOAD:
                log.log(__name__, sys._getframe().f_code.co_name, 'Action type: move', log.LEVEL_DEBUG)
                ManageDownload.move_file(object_id, action)
            elif action.action_type_id == Action.ACTION_UNRAR_PACKAGE:
                log.log(__name__, sys._getframe().f_code.co_name, 'Action type: unrar', log.LEVEL_DEBUG)
                ManageDownload.unrar(object_id, action)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Action is none', log.LEVEL_ERROR)

    def start_multi_downloads(self, file_path):
        download = ManageDownload.get_download_to_start(None, file_path)

        while not self.stop_loop_file_treatment and download is not None:
            log.init('log_download_id_%d.log', download)
            # log.init_log_file('log_download_id_%d.log', config.application_configuration.python_log_format)

            log.log(__name__, sys._getframe().f_code.co_name, '=========> Start new download <=========', log.LEVEL_INFO)
            if config.RESCUE_MODE is False:
                config.application_configuration = ManageDownload.get_application_configuration_by_id(config.application_configuration.id_application, download)
                if config.application_configuration is None:
                    log.init('log_download_id_%d.log', download)
                    # on utilise la nouvelle configuration pour le log console
                    # log.init_log_console(config.application_configuration.python_log_format)
                    # on initialise le log qui sera utilise pour envoyer directement a l'ihm
                    # log.init_log_stream(config.application_configuration.python_log_format)
            else:
                # si on est en rescue mode on a pas acces a la base donc on considere que le telechargement est active
                config.application_configuration = ApplicationConfiguration()
                config.application_configuration.download_activated = True

            if config.application_configuration.download_activated:
                download = ManageDownload.start_download(download)

                # mark link with # in file
                if download.status == Download.STATUS_FINISHED:
                    #change the file permission
                    log.log(__name__, sys._getframe().f_code.co_name, "Change file permission %s" % download.directory.path + download.name, log.LEVEL_INFO, True, download)
                    os.chmod(download.directory.path + download.name, 0o777)

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

                    log.log(__name__, sys._getframe().f_code.co_name, "Updated by start_file_treatment method", log.LEVEL_DEBUG, True, download)

                    #change the file permission
                    # log.log(__name__, sys._getframe().f_code.co_name, "Change file permission", log.LEVEL_INFO, True, download)
                    # os.chmod(download.directory.path + download.name, 0o777)
                log.log(__name__, sys._getframe().f_code.co_name, '=========< End download >=========', log.LEVEL_INFO)
                # next download
                download = ManageDownload.get_download_to_start(None, file_path)
            else:
                log.log(__name__, sys._getframe().f_code.co_name, 'Wait 60 seconds...', log.LEVEL_INFO, True, download)
                # on attend 60s avant de retenter un telechargement
                time.sleep(60)

    def stop_current_downloads(self):
        download_list = ManageDownload.get_downloads_in_progress()

        for download in download_list:
            ManageDownload.stop_download(download)

    def stop_multi_downloads(self, file_path):
        # TODO: stop current download
        self.stop_loop_file_treatment = True

    @staticmethod
    def check_download_alive(download_id):
        download_to_check = ManageDownload.get_download_by_id(download_id)
        ManageDownload.check_download_alive(download_to_check)

    @staticmethod
    def check_multi_downloads_alive():
        downloads = ManageDownload.get_downloads_in_progress()

        for download_to_check in downloads:
            ManageDownload.check_download_alive(download_to_check)

    @staticmethod
    def reset(download_id, file_to_delete):
        download = ManageDownload.get_download_by_id(download_id)

        if download is not None:
            if file_to_delete:
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)

            Treatment.reset_link_finished_in_file(download)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Download is None', log.LEVEL_ERROR)

    @staticmethod
    def delete_package_files(package_id):
        package = ManageDownload.get_package_by_id(package_id)
        list_downloads = ManageDownload.get_downloads_by_package(package)

        for download in list_downloads:
            try:
                download.log = 'deleting file'
                download.status = Download.STATUS_FILE_DELETING
                ManageDownload.update_download(download, True)
                file_path = os.path.join(download.directory.path, download.name)
                os.remove(file_path)
                download.log = 'delete file ok'
                download.status = Download.STATUS_FILE_DELETED
                ManageDownload.update_download(download, True)
            except OSError:
                download.log = 'delete file error'
                download.status = Download.STATUS_FILE_DELETE_ERROR
                ManageDownload.update_download(download, True, force_update_log=True)

    @staticmethod
    def update_plowshare():
        subprocess.call([os.path.abspath(os.path.dirname(sys.argv[0])) + '/scripts/update_plowshare.sh'])
