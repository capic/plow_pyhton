# coding: utf8
# !/usr/bin/env python

from __future__ import unicode_literals

__author__ = 'Vincent'

import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
import requests
import utils
import log
import config
from bean.downloadBean import Download
from bean.actionBean import Action
from bean.downloadPackageBean import DownloadPackage
from bean.downloadDirectoryBean import DownloadDirectory
from bean.downloadHostBean import DownloadHost

import sys
import inspect


class ManageDownload:
    COMMAND_DOWNLOAD = "/usr/bin/plowdown -r 10 -x --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"
    COMMAND_DOWNLOAD_INFOS = "/usr/bin/plowprobe --printf '==>%%f=$=%%s=$=%%m' %s"
    COMMAND_UNRAR = "cd \"%s\" && unrar x -o+ \"%s\""
    MARK_AS_FINISHED = "# FINNISHED "
    MARK_AS_ERROR = "# ERROR"

    def __init__(self):
        # unirest.timeout(config.DEFAULT_UNIREST_TIMEOUT)
        self.action_update_in_progress = False

    def insert_action(self, action):
        log.log('  *** insert_action ***', log.LEVEL_INFO)

        if action is not None:
            try:
                log.log("Insert action ....", log.LEVEL_INFO)
                log.log("Action %s" % action.to_insert_json(), log.LEVEL_DEBUG)
                log.log(config.REST_ADRESSE + 'actions \r\n params: %s' % action.to_insert_json(), log.LEVEL_DEBUG)
                response = requests.post(config.REST_ADRESSE + 'actions',
                                        data=action.to_insert_json())

                if response.status_code != 200:
                    log.log('Error insert actop, %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('Error insert actop, %s => %s' % (response.status_code, response.json()))
            except Exception:
                import traceback
                log.log("Insert action: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            logging.error("action is none")

    def insert_download(self, download):
        log.log('  *** insert_download ***', log.LEVEL_INFO)

        if download is not None:
            download_package = None

            try:
                log.log("Insert host ....", log.LEVEL_INFO)
                log.log("Host %s" % download.host.to_insert_json(), log.LEVEL_DEBUG)
                log.log(config.REST_ADRESSE + 'downloadHosts \r\n params: %s' % download.host.to_insert_json(), log.LEVEL_DEBUG)
                response = requests.post(config.REST_ADRESSE + 'downloadHosts',
                                        data=download.host.to_insert_json())

                if response.status_code != 200:
                    log.log('Error insert host %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('Error insert host %s => %s' % (response.status_code, response.json()))

                download.host = utils.json_to_download_host_object(response.json())

                if utils.package_name_from_download_name(download.name) is not None:
                    download_package = DownloadPackage()
                    download_package.name = utils.package_name_from_download_name(download.name)

                    log.log("Insert package ....", log.LEVEL_INFO)
                    log.log(config.REST_ADRESSE + 'downloads/package \r\n params: %s' % download_package.to_insert_json(), log.LEVEL_DEBUG)
                    response = requests.post(config.REST_ADRESSE + 'downloads/package',
                                            data=download_package.to_insert_json())

                    if response.status_code != 200:
                        log.log('Error insert package %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                        raise Exception('Error insert package %s => %s' % (response.status_code, response.json()))

                    download_package = utils.json_to_download_package_object(response.json())
                    log.log('package inserted: ' + download_package.to_string(), log.LEVEL_DEBUG)

                download.package = download_package

                download.lifecycle_insert_date = datetime.utcnow().isoformat()
                download.lifecycle_update_date = datetime.utcnow().isoformat()
                download.theorical_start_datetime = datetime.utcnow().isoformat()

                log.log("Insert download ....", log.LEVEL_INFO)
                log.log(config.REST_ADRESSE + 'downloads \r\n params: %s' % download.to_insert_json(), log.LEVEL_DEBUG)
                response = requests.post(config.REST_ADRESSE + 'downloads',
                                        data=download.to_insert_json())

                if response.status_code != 200:
                    log.log('Error insert %s => %s' % (response.code, response.json()), log.LEVEL_ERROR)
                    raise Exception('Error insert %s => %s' % (response.status_code, response.json()))
                else:
                    download = self.get_download_by_id(response.json()['id'])

            except Exception:
                import traceback
                log.log("Insert download: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            logging.error("Download is none")

        return download

    def update_download(self, download, force_update_log=False, timeout=None):
        log.log('  *** update_download ***', log.LEVEL_INFO)

        # if timeout is None:
        #     unirest.timeout(config.FAST_UNIREST_TIMEOUT)
        # else:
        #     unirest.timeout(timeout)

        download.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            log.log(config.REST_ADRESSE + 'downloads/' + str(download.id) + '\r\n %s' % download.to_update_object(), log.LEVEL_DEBUG)
            response = requests.put(config.REST_ADRESSE + 'downloads/' + str(download.id),
                                   data=download.to_update_object())

            if response.code != 200:
                log.log('Error update %s => %s' % (response.code, response.json()), log.LEVEL_ERROR)
                download.logs = "ERROR DURING DOWNLOAD UPDATE\r\n"

            self.update_download_log(download, force_update_log)

            # unirest.timeout(config.DEFAULT_UNIREST_TIMEOUT)

        except Exception:
            import traceback
            log.log("Update download: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
            download.logs = traceback.format_exc().splitlines()[-1]
            self.update_download_log(download, True)
            raise
    
    def get_application_configuration_by_id(self, application_configuration_id):
        log.log('   *** get_application_configuration_by_id ***', log.LEVEL_INFO)
        application_configuration = None

        if application_configuration_id is not None:
            try:
                log.log(config.REST_ADRESSE + 'applicationConfiguration/'  + str(application_configuration_id), log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'applicationConfiguration/' + str(application_configuration_id))

                if response.status_code == 200:
                    log.log('application_configuration got: %s' % response.json(), log.LEVEL_DEBUG)
                    application_configuration = utils.json_to_application_configuration_object(response.json())
                else:
                    log.log('Error get %s => %s' % (response.code, response.json()), log.LEVEL_ERROR)
            except Exception:
                import traceback
                log.log("Get application_configuration by id: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            logging.error('Id is none')

        return application_configuration
    
    def update_download_log(self, download, force=False):
        if (config.LOG_BDD is True or force) and download.logs != "":
            try:
                log.log(config.REST_ADRESSE + 'downloads/logs/' + str(download.id) + '\r\n params: %s' % {"id": download.id, "logs": download.logs}, log.LEVEL_DEBUG)
                response = requests.put(config.REST_ADRESSE + 'downloads/logs/' + str(download.id),
                                       data={"id": download.id, "logs": download.logs})

                if response.status_code != 200:
                    log.log('Error update %s => %s' % (response.code, response.json()), log.LEVEL_ERROR)
            except Exception:
                import traceback
                log.log("Update download log: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

    def update_action_callback(self, response):
        log.log('*** update_action_callback ***', log.LEVEL_INFO)
        self.action_update_in_progress = False

    def update_action(self, action):
        log.log('*** update_action ***', log.LEVEL_INFO)

        self.action_update_in_progress = True

        action.lifecycle_update_date = datetime.utcnow().isoformat()
        try:
            log.log(config.REST_ADRESSE + 'actions/' + str(action.id) + '\r\n params: %s' % utils.action_object_to_update_json(action), log.LEVEL_DEBUG)
            requests.put(
                config.REST_ADRESSE + 'actions/' + str(action.id),
                data=utils.action_object_to_update_json(action))
            if response.status_code != 200:
                update_action_callback(response)
            # log.log_debug('Error update %s => %s' % (response.code, response.json())
            # else:
            # action_property_returned = utils.json_to_action_object(response.json())
        except Exception:
            import traceback
            log.log("Update action: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

    def get_download_by_id(self, download_id):
        log.log('   *** get_download_by_id ***', log.LEVEL_INFO)
        download = None

        if download_id is not None:
            try:
                log.log(config.REST_ADRESSE + 'downloads/' + str(download_id), log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads/' + str(download_id))

                if response.status_code == 200:
                    log.log('download got: %s' % response.json(), log.LEVEL_DEBUG)
                    download = utils.json_to_download_object(response.json())
                else:
                    log.log('Error get %s => %s' % (response.code, response.json()), log.LEVEL_ERROR)
            except Exception:
                import traceback
                log.log("Get download by id: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            logging.error('Id is none')

        return download

    def get_package_by_id(self, package_id):
        log.log('   *** get_package_by_id ***', log.LEVEL_INFO)
        package = None

        if package_id is not None:
            try:
                log.log(config.REST_ADRESSE + 'downloads/package/' + str(package_id), log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads/package/' + str(package_id))

                if response.status_code == 200:
                    package = utils.json_to_download_package_object(response.json())
                else:
                    log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
            except Exception:
                import traceback
                log.log("Get download by id: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            logging.error('Id is none')

        return package

    def get_download_directory_by_id(self, directory_id):
        log.log('*** get_download_directory_by_id ***', log.LEVEL_INFO)
        directory = None

        if directory_id is not None:
            try:
                log.log(config.REST_ADRESSE + 'downloadDirectories/' + str(directory_id), log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloadDirectories/' + str(directory_id))

                if response.status_code == 200:
                    directory = utils.json_to_download_directory_object(response.json())
                else:
                    log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
            except Exception:
                import traceback
                log.log("Get download directory by id: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('Id is none', log.LEVEL_ERROR)

        return directory

    def get_actions_by_parameters(self, download_id=None, action_type_id=None):
        log.log('*** get_action_by_parameters ***', log.LEVEL_INFO)
        action_list = None

        try:
            params = {}
            if download_id is not None:
                params['download_id'] = download_id
            if action_type_id is not None:
                params['action_type_id'] = action_type_id

            action_list = []
            log.log(config.REST_ADRESSE + 'actions \r\n params: %s' % params, log.LEVEL_DEBUG)
            response = requests.get(config.REST_ADRESSE + 'actions', params=params)
            if response.status_code == 200:
                action_list = utils.json_to_action_object_list(response.json())
            else:
                log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)

        except Exception:
            import traceback
            log.log("Get action: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        return action_list

    def get_action_by_id(self, action_id):
        log.log('*** get_action_by_id ***', log.LEVEL_INFO)
        action = None

        if action_id is not None:
            try:
                log.log(config.REST_ADRESSE + 'actions/' + str(action_id), log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'actions/' + str(action_id))

                if response.status_code == 200:
                    log.log('Action got: %s' % response.json(), log.LEVEL_DEBUG)
                    action = utils.json_to_action_object(response.json())
                else:
                    log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
            except Exception:
                import traceback
                log.log("Get action: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('Id is none', log.LEVEL_ERROR)

        return action

    def get_download_by_link_file_path(self, link, file_path):
        log.log('   *** get_download_by_link_file_path ***', log.LEVEL_INFO)
        log.log('link: %s, file_path: %s' % (link, file_path), log.LEVEL_DEBUG)

        download = None

        try:
            if link is not None and link != '' and file_path is not None and file_path != '':
                log.log(config.REST_ADRESSE + 'downloads \r\n params: %s' % {"link": link, "file_path": file_path}, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads',
                                       params={"link": link, "file_path": file_path})

                downloads_list = []
                if response.status_code == 200:
                    downloads_list = utils.json_to_download_object_list(response.json())
                else:
                    log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)

                if len(downloads_list) == 0:
                    log.log('No download found with link %s and file_path %s' % (link, file_path), log.LEVEL_INFO)
                elif len(downloads_list) == 1:
                    download = downloads_list[0]
                    log.log('download : %s' % (download.to_string()), log.LEVEL_DEBUG)
                else:
                    download = downloads_list[0]
                    log.log('Too many download found with link %s and file_path %s' % (link, file_path), log.LEVEL_ERROR)

        except Exception:
            import traceback
            log.log("Get download by link file path: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        return download

    def get_downloads_by_package(self, package_id):
        log.log('   *** get_downloads_by_package ***', log.LEVEL_INFO)

        downloads_list = None

        try:
            if package_id is not None:
                log.log(config.REST_ADRESSE + 'downloads \r\n params: %s' % {"package_id": package_id}, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads',
                                       params={"package_id": package_id})

                downloads_list = []
                if response.status_code == 200:
                    downloads_list = utils.json_to_download_object_list(response.json())
                else:
                    log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)

                if len(downloads_list) == 0:
                    logging.info('No download found with package_id %s' % str(package_id))
        except Exception:
            import traceback
            log.log("Get download by package: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        return downloads_list


    def get_download_to_start(self, download_id, file_path=None):
        log.log(' *** get_download_to_start ***', log.LEVEL_INFO)

        download = None

        if download_id is None:
            already_downloaded = True

            while already_downloaded is True:
                already_downloaded = False
                try:
                    if file_path is not None:
                        log.log(config.REST_ADRESSE + 'downloads/next \r\n params: %s' % {"file_path": file_path}, log.LEVEL_DEBUG)
                        response = requests.get(config.REST_ADRESSE + 'downloads/next', params={"file_path": file_path})
                    else:
                        log.log(config.REST_ADRESSE + 'downloads/next', log.LEVEL_DEBUG)
                        response = requests.get(config.REST_ADRESSE + 'downloads/next',
                                               headers={"Accept": "application/json"})

                    if response.status_code == 200:
                        log.log("json: %s" % response.json(), log.LEVEL_DEBUG)
                        download = utils.json_to_download_object(response.json())

                        if download is not None:
                            if '# %s \r\n%s %s' % (download.name, self.MARK_AS_FINISHED, download.link) in open(download.file_path).read():
                                log.log('Download got already downloaded in file => update to finish in database', log.LEVEL_INFO)
                                download.status = Download.STATUS_FINISHED
                                download.size_file_downloaded = download.size_file
                                self.update_download(download)
                                already_downloaded = True
                    else:
                        log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)

                    config.RESCUE_MODE = False
                except Exception:
                    import traceback
                    log.log("no database connection => use rescue mode \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                    log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

                    file = open(file_path, 'r')
                    for line in file:
                        line = line.decode("utf-8")
                        if 'http' in line:
                            log.log('Line %s contains http' % line, log.LEVEL_DEBUG)
                            if not line.startswith('#'):
                                line = line.replace('\n', '')
                                line = line.replace('\r', '')
                                download = Download()
                                download.link = line
                                download.name = "UNKNOWN"
                                download.file_path = file_path
                                break

                    file.close()
                    config.RESCUE_MODE = True
                    log.log('===== Rescue Mode Activated =====', log.LEVEL_INFO)

        else:
            download = self.get_download_by_id(download_id)

        return download


    def get_downloads_in_progress(self):
        log.log('*** get_downloads_in_progress ***', log.LEVEL_INFO)

        try:
            log.log(config.REST_ADRESSE + 'downloads \r\n params: %s' % {"status": Download.STATUS_IN_PROGRESS}, log.LEVEL_DEBUG)
            response = requests.get(config.REST_ADRESSE + 'downloads',
                                   params={"status": Download.STATUS_IN_PROGRESS})

            downloads_list = []
            if response.code == 200:
                downloads_list = utils.json_to_download_object_list(response.json())
            else:
                log.log('Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
        except Exception:
            import traceback
            log.log("Get download in progress: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        return downloads_list


    def download_already_exists(self, link):
        log.log('*** download_already_exists ***', log.LEVEL_INFO)

        # on considere apr defaut que le download existe pour eviter de telecharger si jamais on a pas acces ?
        exists = True

        try:
            if link is not None and link != '':
                log.log(config.REST_ADRESSE + 'downloads \r\n params: %s' % {"link": link}, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads', params={"link": link})
                exists = len(response.json()) > 0
                log.log('download exists ? %s' % str(exists), log.LEVEL_DEBUG)
            else:
                logging.error('Link is none')
        except Exception:
            import traceback
            log.log("Download already exists: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log("Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        return exists

    def insert_update_download(self, link, file_path):
        log.log('*** insert_update_download ***', log.LEVEL_INFO)

        # download = None

        # si la ligne n'est pas marque comme termine avec ce programme
        if not link.startswith(self.MARK_AS_FINISHED):
            if not link.startswith(self.MARK_AS_ERROR):
                link = link.replace('\n', '')
                link = link.replace('\r', '')

                finished = False
                # si la ligne est marque comme termine par le traitement par liste de plowdown
                if link.startswith('#OK'):
                    finished = True
                    link = link.replace('#OK ', '')

                cmd = (self.COMMAND_DOWNLOAD_INFOS % link)
                #exists = self.download_already_exists(link)
                download = self.get_download_by_link_file_path(link, file_path)
                # on n'insere pas un lien qui existe deja ou qui est termine
                if config.RESCUE_MODE is False and download is None:
                    log.log('Download finished ? %s' % (str(finished)), log.LEVEL_DEBUG)
                    if not finished:
                        log.log('Download %s doesn''t exist -> insert' % link, log.LEVEL_DEBUG)
                        log.log('command : %s' % cmd, log.LEVEL_DEBUG)

                        name, size, host = utils.get_infos_plowprobe(cmd)
                        if name is not None:
                            log.log('Infos get from plowprobe %s' % name, log.LEVEL_DEBUG)

                            download_host = DownloadHost()
                            download_host.name = host

                            download_directory = DownloadDirectory()
                            download_directory.id = config.DIRECTORY_DOWNLOAD_DESTINATION_ID
                            download_directory.path = config.DIRECTORY_DOWNLOAD_DESTINATION

                            download = Download()
                            download.name = name
                            download.host = download_host
                            download.link = link
                            download.size = size
                            download.status = Download.STATUS_WAITING
                            download.priority = Download.PRIORITY_NORMAL
                            download.file_path = file_path
                            download.directory = download_directory
                            download.lifecycle_insert_date = datetime.utcnow().isoformat()

                            self.insert_download(download)
            else:
                link = link.replace('\n', '')
                link = link.replace('\r', '')
                link = link.replace(self.MARK_AS_FINISHED + ' ', '')
                log.log('Download already marked as finished in file', log.LEVEL_INFO)
                download = self.get_download_by_link_file_path(link, file_path)
                if download is not None:
                    if download.status != Download.STATUS_FINISHED:
                        log.log('Download status is not finised => To update', log.LEVEL_DEBUG)

                        if download.name is None or download.name == '':
                            cmd = (self.COMMAND_DOWNLOAD_INFOS % link)
                            log.log('command : %s' % cmd, log.LEVEL_DEBUG)
                            name, size = utils.get_infos_plowprobe(cmd)
                            log.log('Infos get from plowprobe %s,%s' % (
                                name, size), log.LEVEL_DEBUG)
                            to_update = True

                        action_bool = False
                        # si on a des actions en cours ou des termines on ne change pas le statut
                        actions_list = self.get_actions_by_parameters(download.id)
                        for action in actions_list:
                            if action.status != Action.STATUS_WAITING:
                                action_bool = True
                                break

                        if finished and not action_bool:
                            download.status = Download.STATUS_FINISHED
                            to_update = True

                        if to_update:
                            download.logs = 'updated by insert_update_download method\r\n'
                            self.update_download(download)
        else:
            link = link.replace('\n', '')
            link = link.replace('\r', '')
            link = link.replace(self.MARK_AS_FINISHED + ' ', '')
            log.log('Download already marked as finished in file', log.LEVEL_INFO)
            download = self.get_download_by_link_file_path(link, file_path)
            if download is not None:
                if download.status != Download.STATUS_FINISHED:
                    log.log('Download status is not finised => To update', log.LEVEL_INFO)

                    if download.name is None or download.name == '':
                        cmd = (self.COMMAND_DOWNLOAD_INFOS % link)
                        log.log('command : %s' % cmd, log.LEVEL_DEBUG)
                        name, size = utils.get_infos_plowprobe(cmd)
                        log.log('Infos get from plowprobe %s,%s' % (name, size), log.LEVEL_DEBUG)

                    download.status = Download.STATUS_FINISHED

                    self.update_download(download)

        return download

    def stop_download(self, download):
        log.log('*** stop_download ***', log.LEVEL_INFO)
        log.log('pid python: %s' % str(download.pid_python), log.LEVEL_DEBUG)
        utils.kill_proc_tree(download.pid_python)
        utils.kill_proc_tree(download.pid_plowdown)

        download.pid_python = 0
        download.pid_plowdown = 0
        download.status = Download.STATUS_WAITING
        download.logs = 'updated by stop_download method\r\n'
        self.update_download(download)

    def start_download(self, download):
        log.log('*** start_download ***', log.LEVEL_INFO)
        indent_log = '  '

        cmd = (
            self.COMMAND_DOWNLOAD % (
                config.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, config.DIRECTORY_DOWNLOAD_DESTINATION, download.link))
        log.log('%s command : %s' % (indent_log, cmd), log.LEVEL_DEBUG)
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        download.pid_plowdown = p.pid
        download.pid_python = os.getpid()
        download.status = Download.STATUS_IN_PROGRESS
        download.logs = 'updated by start_download method\r\n'
        if config.RESCUE_MODE is False:
            self.update_download(download)

        line = ''
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() is not None:
                break
            if out != '':
                if out != '\n' and out != '\r':
                    line += out
                else:
                    line = utils.clean_plowdown_line(line)
                    download = self.get_download_values(line, download)
                    line = ''

        return download

    # 0 => pourcentage, 1 => taille totale, 2 => pourcentage recu, 3 => taille recu, 4 pourcentage transfere, 5 => taille transfere,
    # 6 => vitesse moyenne recu, 7 => vitesse moyenne envoye, 8 => temps total, 9 => temps passe, 10 => temps restant, 11 => vitesse courante
    def get_download_values(self, values_line, download):
        log.log('*** get_download_values ***', log.LEVEL_INFO)

        download_log = ''
        timeout = None

        log.log("Rescue mode: %s" % str(config.RESCUE_MODE), log.LEVEL_INFO)
        log.log(values_line, log.LEVEL_DEBUG)
        values = values_line.split()

        if len(values) > 0:
            if values[0].isdigit():
                # progress part
                download.progress_part = int(values[2])

                if download.size_file is None or download.size_file == 0:
                    # size file
                    download.size_file = utils.compute_size(values[1])

                # size part
                download.size_part = utils.compute_size(values[1])

                # size part downloaded
                download.size_part_downloaded = utils.compute_size(values[3])
                # size file downloaded
                download_size_file_downloaded = download.size_part_downloaded
                if download.size_file > 0:
                    download_size_file_downloaded = (
                                                        download.size_file - download.size_part) + download.size_part_downloaded
                download.size_file_downloaded = download_size_file_downloaded

                # average speed
                download.average_speed = utils.compute_size(values[6])

                # current speed
                download.current_speed = utils.compute_size(values[11])

                if '-' not in values[9]:
                    # time spent
                    download.time_spent = utils.hms_to_seconds(values[9])

                if '-' not in values[10]:
                    # time left
                    download.time_left = utils.hms_to_seconds(values[10])

                if values[1] == values[3] and values[1] != '0' and download.status == Download.STATUS_IN_PROGRESS:
                    log.log('download will be marked as finished', log.LEVEL_INFO)
                    download.status = Download.STATUS_FINISHED
                    directory = DownloadDirectory()
                    directory.id = config.DIRECTORY_DOWNLOAD_DESTINATION_ID
                    directory.path = config.DIRECTORY_DOWNLOAD_DESTINATION
                    download.directory = directory
                    download.to_move_directory = None
                    timeout = config.DEFAULT_UNIREST_TIMEOUT

            elif "Filename" in values[0]:
                tab_name = values_line.split('Filename:')
                download.name = utils.clean_string_console(tab_name[len(tab_name) - 1])
            elif "Waiting" in values[0]:
                download.theorical_start_datetime = (datetime.utcnow() + timedelta(0, int(values[1]))).isoformat()
                download_log += 'Theorical start date time %s \r\n' % str(download.theorical_start_datetime)
            elif "Link" in values[0] and "is" in values[1] and "not" in values[2] and "alive" in values[3]:
                download_log += 'Link is not alive'
                download.status = Download.STATUS_ERROR

            download_log += time.strftime('%d/%m/%y %H:%M:%S',
                                 time.localtime()) + ': ' + values_line + '\r\n'
            download.logs = download_log

            # si on est pas en rescue mode
            if config.RESCUE_MODE is False:
                try:
                    self.update_download(download, timeout)
                except Exception:
                    if download.status == Download.STATUS_FINISHED:
                        config.RESCUE_MODE = True

        return download


    def check_download_alive(self, download):
        log.log('*** check_download_alive ***', log.LEVEL_INFO)

        if not utils.check_pid(download.pid_plowdown):
            # utils.kill_proc_tree(download.pid_python)
            log.log('Process %s for download %s killed for inactivity ...\r\n' % (
                str(download.pid_python), download.name), log.LEVEL_DEBUG)

            download.pid_plowdown = 0
            download.pid_python = 0
            download.status = Download.STATUS_WAITING
            download.time_left = 0
            download.average_speed = 0
            download.logs = 'updated by check_download_alive_method\r\nProcess killed by inactivity ...\r\n'

            self.update_download(download)

    def move_file(self, download_id, action):
        log.log('*** move_file ***', log.LEVEL_INFO)

        if action is not None:
            download = self.get_download_by_id(download_id)

            if download is not None:
                action_directory_src = utils.find_element_by_attribute_in_object_array(action.properties, 'property_id', Action.PROPERTY_DIRECTORY_SRC)
                src_file_path = os.path.join(action_directory_src.directory.path, download.name)
                log.log('Source path %s' % src_file_path, log.LEVEL_DEBUG)

                action_directory_dst = utils.find_element_by_attribute_in_object_array(action.properties, 'property_id', Action.PROPERTY_DIRECTORY_DST)
                dst_file_path = os.path.join(action_directory_dst.directory.path, download.name)
                log.log('Destination path %s' % dst_file_path, log.LEVEL_DEBUG)

                if action_directory_src.directory.id != action_directory_dst.directory.id:
                    if os.path.isfile(src_file_path):
                        log.log('downloaded file exists', log.LEVEL_DEBUG)
                        download.status = Download.STATUS_MOVING
                        download.logs = 'File %s exists\r\n' % src_file_path
                        download.logs += 'Moving from %s to %s => status %s\r\n' % (src_file_path, dst_file_path, download.status)
                        self.update_download(download)

                        try:
                            utils.copy_large_file(src_file_path, dst_file_path, action, Action.STATUS_IN_PROGRESS,
                                                  self.treatment_update_action)

                            self.action_update_in_progress = False
                            self.treatment_update_action(action, Action.STATUS_FINISHED, 100, 0, None)
                            download.status = Download.STATUS_MOVED
                            download.directory = action_directory_dst.directory
                            download.logs = 'File moved to %s => status %s\r\n' % (download.directory.path, download.status)
                            self.update_download(download)
                        except Exception:
                            import traceback
                            log.log(traceback.format_exc(), log.LEVEL_ERROR)
                            download.status = Download.STATUS_ERROR_MOVING
                            download.logs = 'File moved to %s => status %s\r\n' % (download.directory.path, download.status)
                            self.update_download(download, force_update_log=True)
                    else:
                        log.log('File does not exist', log.LEVEL_ERROR)
                        download.logs = 'File %s does not exist\r\n' % src_file_path
                        self.update_download_log(download)
                else:
                    log.log('Sames source and destination directories', log.LEVEL_ERROR)
            else:
                log.log('Download is none', log.LEVEL_ERROR)
        else:
            log.log('Action is none', log.LEVEL_ERROR)

    def treatment_update_action(self, action, status, percent, time_left, time_elapsed):
        log.log\
            ('*** treatment_update_action ***', log.LEVEL_INFO)

        action_returned = None
        if not self.action_update_in_progress:
            if percent is not None:
                utils.change_action_property(action, 'property_id', Action.PROPERTY_PERCENTAGE, 'property_value', percent)

            if time_left is not None:
                utils.change_action_property(action, 'property_id', Action.PROPERTY_TIME_LEFT, 'property_value', time_left)

            if time_elapsed is not None:
                utils.change_action_property(action, 'property_id', Action.PROPERTY_TIME_ELAPSED, 'property_value', time_elapsed)

            if status is not None:
                action.action_status_id = status

            self.update_action(action)

        return action_returned

    def unrar(self, object_id, action):
        log.log('*** unrar ***', log.LEVEL_INFO)

        # logger = logging.getLogger()
        # logger.setLevel(logging.DEBUG)
        #
        # file_handler = logging.FileHandler(config.DIRECTORY_WEB_LOG + 'log_unrar_id_' + str(download_id) + '.log')
        # file_handler.setLevel(logging.DEBUG)
        # file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        # logger.addHandler(file_handler)

        downloads_list = self.get_downloads_by_package(object_id)
        if downloads_list is not None and len(downloads_list) > 0:
            def getKey(d):
                return d.name

            downloads_list = sorted(downloads_list, key=getKey)
            download = downloads_list[0]

            filename, file_extension = os.path.splitext(download.name)
            if file_extension == '.rar':
                for down in downloads_list:
                    down.status = Download.STATUS_UNRARING
                    self.update_download(down)

                download.logs = 'Unrar in progress ... \r\n'
                self.update_download_log(download)
                if not utils.is_this_running("[u]nrar x \"%s\"" % download.name):
                    cmd = (
                        self.COMMAND_UNRAR % (
                            download.directory.path, download.name))

                    download.logs += 'Command: %s\r\n' % cmd
                    self.update_download_log(download)
                    log.log('command : %s' % cmd, log.LEVEL_DEBUG)
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                    self.treatment_update_action(action, Action.STATUS_IN_PROGRESS, 0, None, None)

                    line = ''
                    while True:
                        out = p.stdout.read(1)
                        if out == '' and p.poll() is not None:
                            break
                        if out != '':
                            if out != '%':
                                line += out
                            else:
                                log.log('Line %s' % line, log.LEVEL_DEBUG)
                                download.logs = line
                                values = line.split()
                                if len(values) > 1:
                                    percent = values[int(len(values) - 1)]
                                    log.log('percent ' + percent, log.LEVEL_DEBUG)
                                    self.treatment_update_action(action, None, percent, None, None)
                                    self.update_download_log(download)

                    if 'All OK' in line:
                        download.logs = 'Unrar finished, all is OK\r\n'
                        self.treatment_update_action(action, Action.STATUS_FINISHED, 100, None, None)
                        self.update_download_log(download)
                        download_status = Download.STATUS_UNRAR_OK
                    else:
                        download.logs = 'Unrar finised but error\r\n'
                        self.treatment_update_action(action, Action.STATUS_ERROR, None, None, None)
                        self.update_download_log(download)
                        download_status = Download.STATUS_UNRAR_ERROR

                    for down in downloads_list:
                        down.status = download_status
                        self.update_download(down)

    def disconnect(self):
        log.log('*** disconnect ***', log.LEVEL_INFO)
