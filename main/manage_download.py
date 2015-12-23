# coding: utf8
# !/usr/bin/env python

from __future__ import unicode_literals

__author__ = 'Vincent'

import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
import unirest
import utils
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
    COMMAND_MOVE = "pymv \"%s\" \"%s\""
    MARK_AS_FINISHED = "# FINNISHED "
    MARK_AS_ERROR = "# ERROR"

    def __init__(self):
        unirest.timeout(utils.DEFAULT_UNIREST_TIMEOUT)

    def insert_download(self, download):
        utils.log_debug(u'  *** insert_download ***')

        if download is not None:
            download_package = None

            try:
                utils.log_debug("Insert host ....")
                utils.log_debug("Host %s" % download.host.to_insert_json())
                response = unirest.post(utils.REST_ADRESSE + 'downloadHosts',
                                        headers={"Accept": "application/json"},
                                        params=download.host.to_insert_json())

                if response.code != 200:
                    utils.log_debug(u'Error insert host %s => %s' % (response.code, response.body))
                    raise Exception(u'Error insert host %s => %s' % (response.code, response.body))

                download.host = utils.json_to_download_host_object(response.body)

                if utils.package_name_from_download_name(download.name) is not None:
                    download_package = DownloadPackage()
                    download_package.name = utils.package_name_from_download_name(download.name)

                    utils.log_debug("Insert package ....")
                    response = unirest.post(utils.REST_ADRESSE + 'downloads/package',
                                            headers={"Accept": "application/json"},
                                            params=download_package.to_insert_json())

                    if response.code != 200:
                        utils.log_debug(u'Error insert package %s => %s' % (response.code, response.body))
                        raise Exception(u'Error insert package %s => %s' % (response.code, response.body))

                    download_package = utils.json_to_download_package_object(response.body)
                    utils.log_debug(u'package inserted: ' + download_package.to_string())

                download.package = download_package

                utils.log_debug("Insert directory ....")
                response = unirest.post(utils.REST_ADRESSE + 'downloadDirectories',
                                        headers={"Accept": "application/json"},
                                        params=download.to_move_directory.to_insert_json())

                if response.code != 200:
                    utils.log_debug(u'Error insert directory %s => %s' % (response.code, response.body))
                    raise Exception(u'Error insert directory %s => %s' % (response.code, response.body))

                download_directory = utils.json_to_download_directory_object(response.body)
                utils.log_debug(u'directory inserted: ' + download_directory.to_string())

                download.to_move_directory = download_directory
                download.lifecycle_insert_date = datetime.utcnow().isoformat()
                download.lifecycle_update_date = datetime.utcnow().isoformat()
                download.theorical_start_datetime = datetime.utcnow().isoformat()

                utils.log_debug("Insert download ....")
                response = unirest.post(utils.REST_ADRESSE + 'downloads', headers={"Accept": "application/json"},
                                        params=download.to_insert_json())

                if response.code != 200:
                    utils.log_debug(u'Error insert %s => %s' % (response.code, response.body))
                    raise Exception(u'Error insert %s => %s' % (response.code, response.body))

            except Exception:
                utils.log_debug("Insert download: No database connection")
                import traceback

                print(traceback.format_exc())
        else:
            logging.error("Download is none")

    def update_download(self, download):
        utils.log_debug(u'  *** update_download ***')

        download.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            response = unirest.put(utils.REST_ADRESSE + 'downloads/' + str(download.id),
                                   headers={"Accept": "application/json"},
                                   params=download.to_update_object())

            if response.code != 200:
                utils.log_debug(u'Error update %s => %s' % (response.code, response.body))
                download.logs = u"ERROR DURING DOWNLOAD UPDATE"

            self.update_download_log(download)

        except Exception:
            utils.log_debug("Update download: No database connection")
            import traceback

            print(traceback.format_exc())

    def update_download_log(self, download):
        if download.logs != "":
            try:
                response = unirest.put(utils.REST_ADRESSE + 'downloads/logs/' + str(download.id),
                                       headers={"Accept": "application/json"},
                                       params={"id": download.id, "logs": download.logs})

                if response.code != 200:
                    utils.log_debug(u'Error update %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug("Update download log: No database connection")
                import traceback

                print(traceback.format_exc())

    def update_action_property(self, action_property):
        action_property_returned = None

        action_property.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            response = unirest.put(
                utils.REST_ADRESSE + 'actions/' + str(action_property.download_id) + '/' + str(
                    action_property.action_type_id) + '/' + str(action_property.property_id) + '/' + str(
                    action_property.num),
                headers={"Accept": "application/json"},
                params=action_property.to_update_json())
            if response.code != 200:
                utils.log_debug(u'Error update %s => %s' % (response.code, response.body))
            else:
                action_property_returned = utils.json_to_action_object(response.body)
        except Exception:
            utils.log_debug("Update action: No database connection")
            import traceback

            print(traceback.format_exc())

        return action_property_returned

    def get_download_by_id(self, download_id):
        utils.log_debug(u'   *** get_download_by_id ***')
        download = None

        if download_id is not None:
            try:
                response = unirest.get(utils.REST_ADRESSE + 'downloads/' + str(download_id),
                                       headers={"Accept": "application/json"})

                if response.code == 200:
                    download = utils.json_to_download_object(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug("Get download by id: No database connection")
                import traceback

                print(traceback.format_exc())
        else:
            logging.error('Id is none')

        return download

    def get_package_by_id(self, package_id):
        utils.log_debug(u'   *** get_package_by_id ***')
        package = None

        if package_id is not None:
            try:
                response = unirest.get(utils.REST_ADRESSE + 'downloads/package/' + str(package_id),
                                       headers={"Accept": "application/json"})

                if response.code == 200:
                    package = utils.json_to_download_package_object(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug("Get download by id: No database connection")
                import traceback

                print(traceback.format_exc())
        else:
            logging.error('Id is none')

        return package

    def get_download_directory_by_id(self, directory_id):
        utils.log_debug(u'*** get_download_directory_by_id ***')
        directory = None

        if directory_id is not None:
            try:
                response = unirest.get(utils.REST_ADRESSE + 'downloadDirectories/' + str(directory_id),
                                       headers={"Accept": "application/json"})

                if response.code == 200:
                    directory = utils.json_to_download_directory_object(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug("Get download directory by id: No database connection")
                import traceback

                print(traceback.format_exc())
        else:
            logging.error('Id is none')

        return directory

    def get_actions(self, download_id, action_type_id, num):
        utils.log_debug(u'*** get_action ***')
        actions_list = None

        if download_id is not None and action_type_id is not None and num is not None:
            try:
                response = unirest.get(utils.REST_ADRESSE + 'actions',
                                       params={"download_id": download_id, "action_type_id": action_type_id,
                                               "num": num},
                                       headers={"Accept": "application/json"})

                actions_list = []
                if response.code == 200:
                    actions_list = utils.json_to_action_object_list(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug("Get action: No database connection")
                import traceback

                print(traceback.format_exc())

            if len(actions_list) == 0:
                logging.info('No actions found  %s' % actions_list)
        else:
            logging.error('Id is none')

        return actions_list

    def get_download_by_link_file_path(self, link, file_path):
        utils.log_debug(u'   *** get_download_by_link_file_path ***')
        utils.log_debug(u'link: %s, file_path: %s' % (link, file_path))

        download = None

        try:
            if link is not None and link != '' and file_path is not None and file_path != '':
                response = unirest.get(utils.REST_ADRESSE + 'downloads',
                                       headers={"Accept": "application/json"},
                                       params={"link": link, "file_path": file_path})

                downloads_list = []
                if response.code == 200:
                    downloads_list = utils.json_to_download_object_list(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))

                if len(downloads_list) == 0:
                    logging.info('No download found with link %s and file_path %s' % (link, file_path))
                elif len(downloads_list) == 1:
                    download = downloads_list[0]
                    utils.log_debug(u'download : %s' % (download.to_string()))
                else:
                    logging.error('Too many download found with link %s and file_path %s' % (link, file_path))

        except Exception:
            utils.log_debug("Get download by link file path: No database connection")
            import traceback

            print(traceback.format_exc())

        return download


    def get_downloads_by_package(self, package):
        utils.log_debug(u'   *** get_downloads_by_package ***')
        utils.log_debug(u'package: %s' % package.to_string())

        downloads_list = None

        try:
            if package is not None and package != '':
                response = unirest.get(utils.REST_ADRESSE + 'downloads',
                                       headers={"Accept": "application/json"},
                                       params={"package_id": package.id})

                downloads_list = []
                if response.code == 200:
                    downloads_list = utils.json_to_download_object_list(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))

                if len(downloads_list) == 0:
                    logging.info('No download found with package %s' % package)
        except Exception:
            utils.log_debug("Get download by package: No database connection")
            import traceback

            print(traceback.format_exc())

        return downloads_list


    def get_download_to_start(self, download_id, file_path=None):
        utils.log_debug(u' *** get_download_to_start ***')
        utils.log_debug(u'download_id: %s' % str(download_id))

        download = None

        if download_id is None:
            try:
                if file_path is not None:
                    response = unirest.get(utils.REST_ADRESSE + 'downloads/next',
                                           headers={"Accept": "application/json"}, params={"file_path": file_path})
                else:
                    response = unirest.get(utils.REST_ADRESSE + 'downloads/next',
                                           headers={"Accept": "application/json"})

                if response.code == 200:
                    print("json: %s" % response.body)
                    download = utils.json_to_download_object(response.body)
                    print("download: %s" % download.to_string())
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug(u'no database connection => use rescue mode')
                import traceback

                print(traceback.format_exc())
                file = open(file_path, 'r')
                for line in file:
                    line = line.decode("utf-8")
                    if 'http' in line:
                        utils.log_debug(u'Line %s contains http' % line)
                        if not line.startswith('#'):
                            line = line.replace('\n', '')
                            line = line.replace('\r', '')
                            download = Download()
                            download.link = line
                            download.file_path = file_path
                            break

                file.close()

        else:
            download = self.get_download_by_id(download_id)

        return download


    def get_downloads_in_progress(self):
        utils.log_debug(u'*** get_downloads_in_progress ***')

        try:
            response = unirest.get(utils.REST_ADRESSE + 'downloads',
                                   headers={"Accept": "application/json"},
                                   params={"status": Download.STATUS_IN_PROGRESS})

            downloads_list = []
            if response.code == 200:
                downloads_list = utils.json_to_download_object_list(response.body)
            else:
                utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
        except Exception:
            utils.log_debug("Get download in progress: No database connection")
            import traceback

            print(traceback.format_exc())

        return downloads_list


    def download_already_exists(self, link):
        utils.log_debug(u'*** download_already_exists ***')

        exists = False

        try:
            if link is not None and link != '':
                response = unirest.get(utils.REST_ADRESSE + 'downloads', headers={"Accept": "application/json"},
                                       params={"link": link})
                exists = len(response.body) > 0
                utils.log_debug(u'download exists ? %s' % str(exists))
            else:
                logging.error('Link is none')
        except Exception:
            utils.log_debug("Download already exists: No database connection")
            import traceback

            print(traceback.format_exc())

        return exists

    def insert_update_download(self, link, file_path):
        utils.log_debug(u'*** insert_update_download ***')

        download = None

        # si la ligne n'est pas marque comme termine avec ce programme
        if not link.startswith(self.MARK_AS_FINISHED):
            link = link.replace('\n', '')
            link = link.replace('\r', '')

            finished = False
            # si la ligne est marque comme termine par le traitement par liste de plowdown
            if link.startswith('#OK'):
                finished = True
                link = link.replace('#OK ', '')

            cmd = (self.COMMAND_DOWNLOAD_INFOS % link)
            exists = self.download_already_exists(link)
            # on n'insere pas un lien qui existe deja ou qui est termine
            if not exists:
                utils.log_debug(u'Download finished ? %s' % (str(finished)))
                if not finished:
                    utils.log_debug(u'Download %s doesn''t exist -> insert' % link)
                    utils.log_debug(u'command : %s' % cmd)

                    name, size, host = utils.get_infos_plowprobe(cmd)
                    if name is not None:
                        utils.log_debug('Infos get from plowprobe %s' % name)

                        download_host = DownloadHost()
                        download_host.name = host

                        download_directory = DownloadDirectory()
                        download_directory.id = utils.DIRECTORY_DOWNLOAD_DESTINATION_ID
                        download_directory.path = utils.DIRECTORY_DOWNLOAD_DESTINATION

                        download = Download()
                        download.name = name
                        download.host = download_host
                        download.link = link
                        download.size = size
                        download.status = Download.STATUS_WAITING
                        download.priority = Download.PRIORITY_NORMAL
                        download.file_path = file_path
                        download.lifecycle_insert_date = datetime.utcnow().isoformat()
                        download.to_move_directory = download_directory

                        self.insert_download(download)
            else:
                to_update = False
                utils.log_debug(u'Download %s exists -> update' % link)
                download = self.get_download_by_link_file_path(link, file_path)

                if download is not None:
                    if download.status != Download.STATUS_FINISHED:
                        if download.name is None or download.name == '':
                            utils.log_debug(u'command : %s' % cmd)
                            name, size = utils.get_infos_plowprobe(cmd)
                            utils.log_debug(u'Infos get from plowprobe %s,%s' % (
                                name, size))
                            to_update = True

                        if finished:
                            download.status = Download.STATUS_FINISHED
                            to_update = True

                        if to_update:
                            download.logs = 'updated by insert_update_download method\r\n'
                            self.update_download(download)

        return download

    def stop_download(self, download):
        utils.log_debug(u'*** stop_download ***')
        utils.log_debug(u'pid python: %s' % str(download.pid_python))
        utils.kill_proc_tree(download.pid_python)

        download.pid_python = 0
        download.pid_plowdown = 0
        download.status = Download.STATUS_WAITING
        download.logs = 'updated by stop_download method\r\n'
        self.update_download(download)


    def start_download(self, download):
        utils.log_debug(u'*** start_download ***')
        indent_log = '  '

        cmd = (
            self.COMMAND_DOWNLOAD % (
                utils.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, utils.DIRECTORY_DOWNLOAD_DESTINATION, download.link))
        utils.log_debug(u'%s command : %s' % (indent_log, cmd))
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        download.pid_plowdown = p.pid
        download.pid_python = os.getpid()
        download.status = Download.STATUS_IN_PROGRESS
        download.logs = 'updated by start_download method\r\n'
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
                    utils.log_debug(line)
                    download = self.get_download_values(line, download)
                    line = ''

        return download


    # 0 => pourcentage, 1 => taille totale, 2 => pourcentage recu, 3 => taille recu, 4 pourcentage transfere, 5 => taille transfere,
    # 6 => vitesse moyenne recu, 7 => vitesse moyenne envoye, 8 => temps total, 9 => temps passe, 10 => temps restant, 11 => vitesse courante
    def get_download_values(self, values_line, download):
        utils.log_debug(u'*** get_download_values ***')

        log = ''

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
                    utils.log_debug(u'download marked as finished')
                    download.status = Download.STATUS_FINISHED
                    directory = DownloadDirectory()
                    directory.id = utils.DIRECTORY_DOWNLOAD_DESTINATION_ID
                    directory.path = utils.DIRECTORY_DOWNLOAD_DESTINATION
                    download.directory = directory
                    download.to_move_directory = None

            elif "Filename" in values[0]:
                tab_name = values_line.split('Filename:')
                download.name = utils.clean_string_console(tab_name[len(tab_name) - 1])
            elif "Waiting" in values[0]:
                download.theorical_start_datetime = (datetime.utcnow() + timedelta(0, int(values[1]))).isoformat()
                log += 'Theorical start date time %s \r\n' % str(download.theorical_start_datetime)
            elif "Link" in values[0] and "is" in values[1] and "not" in values[2] and "alive" in values[3]:
                log += 'Theorical start date time Link is not alive'
                download.status = Download.STATUS_ERROR

            log += time.strftime('%d/%m/%y %H:%M:%S',
                                 time.localtime()) + ': ' + values_line + '\r\n'
            download.logs = log

            # si on est pas en rescue mode
            if download.id != -1:
                self.update_download(download)

        return download


    def check_download_alive(self, download):
        utils.log_debug(u'*** check_download_alive ***')

        if not utils.check_pid(download.pid_plowdown):
            # utils.kill_proc_tree(download.pid_python)
            utils.log_debug(u'Process %s for download %s killed for inactivity ...\r\n' % (
                str(download.pid_python), download.name))

            download.pid_plowdown = 0
            download.pid_python = 0
            download.status = Download.STATUS_WAITING
            download.time_left = 0
            download.average_speed = 0
            download.logs = 'updated by check_download_alive_method\r\nProcess killed by inactivity ...\r\n'

            self.update_download(download)

    def move_download(self, download):
        utils.log_debug(u'*** move_download ***')

        try:
            unirest.timeout(36000)
            response = unirest.post(utils.REST_ADRESSE + 'downloads/moveOne', headers={"Accept": "application/json"},
                                    params={'id': download.id, 'directory_id': download.to_move_directory.id,
                                            'from': 2})
            unirest.timeout(utils.DEFAULT_UNIREST_TIMEOUT)
            utils.log_debug(u'apres deplacement')

            if response.code != 200:
                utils.log_debug(u'Error during moving file operation %s => %s' % (response.code, response.body))
            else:
                utils.log_debug(u'Moving OK %s => %s' % (str(response.code), response.body))
        except Exception:
            import traceback

            utils.log_debug(traceback.format_exc())

    def move_file(self, actions_list, download):
        utils.log_debug(u'*** move_file ***')

        action_directory_src = utils.get_action_by_property(actions_list, Action.PROPERTY_DIRECTORY_SRC)
        src_file_path = os.path.join(action_directory_src.directory.path, download.name)

        action_directory_dst = utils.get_action_by_property(actions_list, Action.PROPERTY_DIRECTORY_DST)
        download.logs = 'Move file in progress, from %s to %s\r\n' % (
            src_file_path, action_directory_dst.directory.path)
        self.update_download(download)

        if os.path.isfile(src_file_path):
            utils.log_debug(u'downloaded file exists')
            download.logs = 'File %s exists\r\n' % src_file_path
            self.update_download_log(download)

            action_percent = utils.get_action_by_property(actions_list, Action.PROPERTY_PERCENTAGE)

            if not utils.is_this_running(
                            "[p]ymv -g \"%s\" \"%s\"" % (src_file_path, action_directory_dst.directory.path)):
                cmd = (
                    self.COMMAND_MOVE % (
                        src_file_path, action_directory_dst.directory.path))
                download.logs += 'Command: %s\r\n' % cmd
                self.update_download_log(download)
                utils.log_debug(u'command : %s' % cmd)
                # p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, env=dict(COLUMNS='80', LINES='25'))
                #
                # action_percent.property_value = 0
                # self.update_action_property(action_percent)
                #
                # line = ''
                # while True:
                # out = p.stdout.read(1)
                # if out == '' and p.poll() is not None:
                # break
                # if out != '':
                #         if out != '\n' and out != '\r':
                #             line += out
                #         else:
                #             print('Line %s' % line)
                # download.logs = line
                # values = line.split()
                # if len(values) > 1:
                # percent = values[int(len(values) - 1)]
                # print('percent ' + percent)
                # self.update_download_package_unrar_percent(download.package.id, percent)
                #
                # self.update_download_log(download)

                try:
                    pipe = subprocess.Popen(args, bufsize=0,
                                            shell=False,
                                            stdout=None,  # no redirection, child use parent's stdout
                                            stderr=subprocess.PIPE)  # redirection stderr, create a new pipe, from which later we will read

                except Exception as e:  # inspect.stack()[1][3] will get caller function name
                    logging.error(inspect.stack()[1][3] + ' error: ' + str(e))

                while 1:
                    # use read(1), can get wget progress bar like output
                    s = pipe.stderr.read(1)
                    if s:
                        sys.stdout.write(s)
                    if pipe.returncode is None:
                        code = pipe.poll()
                    else:
                        break
            else:
                download.to_move_directory = None
                download.status = Download.STATUS_ERROR_MOVING
                download.logs = 'ERROR: File %s does not exists\r\n' % src_file_path
                self.update_download(download)

                utils.log_debug(u"ERROR: File %s does not exists" % src_file_path)
                print("#ERROR: File %s does not exists#" % src_file_path)

    def unrar(self, downloads_list):
        utils.log_debug(u'*** unrar ***')

        download = downloads_list[0]

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
            utils.log_debug(u'command : %s' % cmd)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            self.update_download_package_unrar_percent(download.package.id, 0)

            line = ''
            while True:
                out = p.stdout.read(1)
                if out == '' and p.poll() is not None:
                    break
                if out != '':
                    if out != '%':
                        line += out
                    else:
                        print('Line %s' % line)
                        download.logs = line
                        values = line.split()
                        if len(values) > 1:
                            percent = values[int(len(values) - 1)]
                            print('percent ' + percent)
                            self.update_download_package_unrar_percent(download.package.id, percent)

                        self.update_download_log(download)

            if 'All OK' in line:
                download.logs = 'Unrar finished, all is OK'
                self.update_download_package_unrar_percent(download.package.id, 100)
                self.update_download_log(download)
                download_status = Download.STATUS_UNRAR_OK
            else:
                download.logs = 'Unrar finised but error'
                self.update_download(download)
                self.update_download_log(download)
                download_status = Download.STATUS_UNRAR_ERROR

            for down in downloads_list:
                down.status = download_status
                self.update_download(down)


    def disconnect(self):
        utils.log_debug(u'*** disconnect ***')
