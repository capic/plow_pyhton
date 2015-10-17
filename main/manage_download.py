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
from bean.downloadPackageBean import DownloadPackage


class ManageDownload:
    COMMAND_DOWNLOAD = "/usr/bin/plowdown -r 10 -x --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"
    COMMAND_DOWNLOAD_INFOS = "/usr/bin/plowprobe --printf '==>%%f=$=%%s' %s"
    COMMAND_UNRAR = "cd %s && unrar x %s"
    MARK_AS_FINISHED = "# FINNISHED "

    def __init__(self):
        unirest.timeout(15)

    def insert_download(self, download):
        utils.log_debug(u'  *** insert_download ***')

        if download is not None:
            download_package = None
            if utils.package_name_from_download_name(download.name) is not None:
                download_package = DownloadPackage()
                download_package.name = utils.package_name_from_download_name(download.name)

                try:
                    response = unirest.post(utils.REST_ADRESSE + 'downloads/package', headers={"Accept": "application/json"},
                                        params=download_package.to_insert_json())

                    if response.code != 200:
                        utils.log_debug(u'Error insert %s => %s' % (response.code, response.body))

                    download_package = utils.json_to_download_package_object(response.body)
                except Exception:
                    import traceback
                    utils.log_debug(traceback.format_exc())

            download.package = download_package
            download.directory = utils.DIRECTORY_DOWNLOAD_DESTINATION
            download.lifecycle_insert_date = datetime.now()
            download.lifecycle_update_date = datetime.now()
            download.theorical_start_datetime = datetime.now()

            try:
                response = unirest.post(utils.REST_ADRESSE + 'downloads', headers={"Accept": "application/json"},
                                        params=download.to_insert_json())

                if response.code != 200:
                    utils.log_debug(u'Error insert %s => %s' % (response.code, response.body))
            except Exception:
                import traceback
                utils.log_debug(traceback.format_exc())
        else:
            logging.error("Download is none")

    def update_download(self, download):
        utils.log_debug(u'  *** update_download ***')

        download.lifecycle_update_date = datetime.now()

        try:
            response = unirest.put(utils.REST_ADRESSE + 'downloads/' + str(download.id),
                                   headers={"Accept": "application/json"},
                                   params=download.to_json())

            if response.code != 200:
                utils.log_debug(u'Error update %s => %s' % (response.code, response.body))
                download.logs = u"ERROR DURING DOWNLOAD UPDATE"

            self.update_download_log(download)

        except Exception:
            import traceback
            utils.log_debug(traceback.format_exc())

    def update_download_log(self, download):
        if download.logs != "":
            response = unirest.put(utils.REST_ADRESSE + 'downloads/logs/' + str(download.id),
                                   headers={"Accept": "application/json"},
                                   params={"id": download.id, "logs": download.logs})

            if response.code != 200:
                utils.log_debug(u'Error update %s => %s' % (response.code, response.body))

    def get_download_by_id(self, download_id):
        utils.log_debug(u'   *** get_download_by_id ***')
        download = None

        if download_id is not None:
            response = unirest.get(utils.REST_ADRESSE + 'downloads/' + download_id,
                                   headers={"Accept": "application/json"})

            if response == 200:
                download = utils.json_to_download_object(response.body)
            else:
                utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
        else:
            logging.error('Id is none')

        return download

    def get_download_by_link_file_path(self, link, file_path):
        utils.log_debug(u'   *** get_download_by_link_file_path ***')
        utils.log_debug(u'link: %s, file_path: %s' % (link, file_path))

        download = None

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

        return download

    def get_downloads_by_package(self, package):
        utils.log_debug(u'   *** get_downloads_by_package ***')
        utils.log_debug(u'package: %s' % package)

        downloads_list = None

        if package is not None and package != '':
            response = unirest.get(utils.REST_ADRESSE + 'downloads',
                                   headers={"Accept": "application/json"},
                                   params={"package": package})

            downloads_list = []
            if response.code == 200:
                downloads_list = utils.json_to_download_object_list(response.body)
            else:
                utils.log_debug(u'Error get %s => %s' % (response.code, response.body))

            if len(downloads_list) == 0:
                logging.info('No download found with package %s' % package)

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
                    download = utils.json_to_download_object(response.body)
                else:
                    utils.log_debug(u'Error get %s => %s' % (response.code, response.body))
            except Exception:
                utils.log_debug(u'no database connection => use rescue mode')
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
                            break

                file.close()

        else:
            download = self.get_download_by_id(download_id)

        return download

    def get_downloads_in_progress(self):
        utils.log_debug(u'*** get_downloads_in_progress ***')

        response = unirest.get(utils.REST_ADRESSE + 'downloads',
                               headers={"Accept": "application/json"}, params={"status": Download.STATUS_IN_PROGRESS})

        downloads_list = []
        if response.code == 200:
            downloads_list = utils.json_to_download_object_list(response.body)
        else:
            utils.log_debug(u'Error get %s => %s' % (response.code, response.body))

        return downloads_list

    def download_already_exists(self, link):
        utils.log_debug(u'*** download_already_exists ***')

        exists = False
        if link is not None and link != '':
            response = unirest.get(utils.REST_ADRESSE + 'downloads', headers={"Accept": "application/json"},
                                   params={"link": link})
            exists = len(response.body) > 0
            utils.log_debug(u'download exists ? %s' % str(exists))
        else:
            logging.error('Link is none')

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

                    name, size = utils.get_infos_plowprobe(cmd)
                    if name is not None:
                        utils.log_debug('Infos get from plowprobe %s' % name)

                        download = Download()
                        download.name = name
                        download.link = link
                        download.size = size
                        download.status = Download.STATUS_WAITING
                        download.priority = Download.PRIORITY_NORMAL
                        download.file_path = file_path
                        download.lifecycle_insert_date = datetime.now()

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

                if values[1] == values[3] and values[1] != '0':
                    utils.log_debug(u'download marked as finished')
                    download.status = Download.STATUS_FINISHED

            elif "Filename" in values[0]:
                tab_name = values_line.split('Filename:')
                download.name = utils.clean_string_console(tab_name[len(tab_name) - 1])
            elif "Waiting" in values[0]:
                download.theorical_start_datetime = datetime.now() + timedelta(0, int(values[1]))
                log += 'Theorical start date time %s' % str(download.theorical_start_datetime)

            log += time.strftime('%d/%m/%y %H:%M:%S',
                                 time.localtime()) + ': ' + values_line + '\r\n'
            download.logs = log

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
        response = unirest.post(utils.REST_ADRESSE + 'downloads/move', headers={"Accept": "application/json"},
                                params={'id': download.id, 'directory': download.directory})

        if response != 200:
            utils.log_debug(u'Error during moving file operation')

    def unrar(self, download):
        download.logs(u'===== UNRAR =====')
        self.update_download_log(download)

        cmd = (
            self.COMMAND_UNRAR % (
                download.directory, download.name))
        utils.log_debug(u'command : %s' % cmd)
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

        line = ''
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() is not None:
                break
            if out != '':
                if out != '\n' and out != '\r':
                    line += out
                else:
                    download.logs(line)
                    self.update_download_log(download)

    def disconnect(self):
        utils.log_debug(u'*** disconnect ***')
