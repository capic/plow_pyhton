# coding: utf8
# !/usr/bin/env python

from __future__ import unicode_literals

__author__ = 'Vincent'

import logging
import os
import subprocess
import time
from datetime import datetime

import utils
from bean.downloadBean import Download

# from websocket import create_connection


class ManageDownload:
    DIRECTORY_DOWNLOAD_DESTINATION_TEMP = "/mnt/HD/HD_a2/telechargement/temp_plowdown/"
    DIRECTORY_DOWNLOAD_DESTINATION = "/mnt/HD/HD_a2/telechargement/"
    COMMAND_DOWNLOAD = "/usr/bin/plowdown -r 10 -x --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"
    COMMAND_DOWNLOAD_INFOS = "/usr/bin/plowprobe --printf '%%f=$=%%s' %s"
    MARK_AS_FINISHED = "# FINNISHED "

    def __init__(self):
        # self.ws = create_connection("ws://192.168.1.200:7070/")
        self.cnx = utils.database_connect()

    def insert_download(self, download):
        utils.log_debug(u'  *** insert_download ***')
        indent_log = '   '

        if download is not None:
            cursor = self.cnx.cursor()

            download.package = utils.package_name_from_download_name(download.name)

            sql = 'INSERT INTO download (name, package, link, size_file, status, file_path, priority, lifecycle_insert_date) values (%s, %s, %s, %s, %s, %s, %s, %s)'
            data = (
                download.name, download.package, download.link, download.size_file, download.status, download.file_path,
                download.priority,
                datetime.now())
            utils.log_debug(u'%s query: %s | data: (%s, %s, %s, %s, %s, %s, %s, %s)' % (
                    indent_log, sql, download.name, download.package,
                    download.link,
                    str(download.size_file), str(download.status), download.file_path,
                    str(download.priority),
                    str(datetime.now())))

            cursor.execute(sql, data)

            cursor.close()
        else:
            logging.error("Download is none")

    def update_download(self, download):
        utils.log_debug(u'  *** update_download ***')
        indent_log = '   '

        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET name = %s, package = %s, link = %s, size_file = %s, size_part = %s, size_file_downloaded = %s, size_part_downloaded = %s,' \
              'status = %s, progress_part = %s, average_speed = %s, current_speed = %s, time_spent = %s, time_left = %s , pid_plowdown = %s, pid_python = %s, priority = %s, ' \
              'file_path = %s, infos_plowdown = concat(ifnull(infos_plowdown,""), %s), lifecycle_update_date = %s WHERE id = %s'
        data = (download.name, download.package, download.link, download.size_file, download.size_part,
                download.size_file_downloaded, download.size_part_downloaded, download.status, download.progress_part,
                download.average_speed, download.current_speed, download.time_spent, download.time_left,
                download.pid_plowdown, download.pid_python, download.priority, download.file_path,
                download.infos_plowdown, datetime.now(), download.id)
        utils.log_debug(u'%s query : %s | data : (%s, %s, %s, %s, %s, %s,%s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (
                indent_log, sql, download.name, download.package,
                download.link,
                str(download.size_file), str(download.size_part),
                str(download.size_file_downloaded), str(download.size_part_downloaded),
                str(download.status), str(download.progress_part),
                str(download.average_speed), str(download.current_speed), str(download.time_spent),
                str(download.time_left),
                str(download.pid_plowdown), str(download.pid_python),
                str(download.priority),
                download.file_path,
                download.infos_plowdown,
                str(datetime.now()), str(download.id)))
        cursor.execute(sql, data)

        cursor.close()

        # self.ws.send(download.infos_plowdown)

    def get_download_by_id(self, download_id):
        utils.log_debug(u'   *** get_download_by_id ***')
        indent_log = '   '
        download = None

        if id is not None:
            cursor = self.cnx.cursor()

            sql = 'SELECT * FROM download WHERE id = %s'
            data = (download_id, )
            utils.log_debug(u'%s query : %s | data : (%s)' % (indent_log, sql, str(download_id)))

            cursor.execute(sql, data)

            list_download = utils.cursor_to_download_object(cursor)

            if len(list_download) == 0:
                logging.info('No download fouud with id %s' % download_id)
            elif len(list_download) == 1:
                download = list_download[0]
                utils.log_debug(u'%s download : %s' % (indent_log, download.to_string()))
            else:
                logging.error('Too many download found with id %s' % download_id)
        else:
            logging.error('Id is none')

        return download

    def get_download_by_link_file_path(self, link, file_path):
        utils.log_debug(u'   *** get_download_by_link_file_path ***')
        indent_log = '   '

        utils.log_debug(u'%s link: %s, file_path: %s' % (indent_log, link, file_path))

        download = None

        if link is not None and link != '' and file_path is not None and file_path != '':
            cursor = self.cnx.cursor()
            sql = 'SELECT * FROM download WHERE link = %s and file_path = %s'
            data = (link, file_path)
            utils.log_debug(u'%s query : %s | data : (%s, %s)' % (indent_log, sql, link, file_path))

            cursor.execute(sql, data)

            list_download = utils.cursor_to_download_object(cursor)

            if len(list_download) == 0:
                logging.info('No download fouud with link %s and file_path %s' % (link, file_path))
            elif len(list_download) == 1:
                download = list_download[0]
                utils.log_debug(u'%s download : %s' % (indent_log, download.to_string()))
            else:
                logging.error('Too many download found with link %s and file_path %s' % (link, file_path))

        return download

    def get_download_to_start(self, download_id, file_path=None):
        utils.log_debug(u' *** get_download_to_start ***')
        indent_log = ' '
        utils.log_debug(u' %s download_id: %s' % (indent_log, str(download_id)))

        download = None

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s'
            under_sql = 'SELECT MAX(priority) FROM download where status = %s'

            if file_path is not None:
                sql += ' AND file_path = %s'
                under_sql += ' AND file_path = %s'

                sql += ' AND priority = (' + under_sql + ')'
                data = (Download.STATUS_WAITING, file_path, Download.STATUS_WAITING, file_path)

                utils.log_debug(u'%s query : %s | data : (%s, %s, %s, %s)' % (
                        indent_log, sql, str(Download.STATUS_WAITING), file_path,
                        str(Download.STATUS_WAITING), file_path))
            else:
                sql += ' AND priority = (' + under_sql + ')'

                data = (Download.STATUS_WAITING, Download.STATUS_WAITING)
                utils.log_debug(u'%s query : %s | data : (%s, %s)' % (indent_log, sql, str(Download.STATUS_WAITING),
                                                         str(Download.STATUS_WAITING)))

            sql += ' HAVING  MIN(id)'

            cursor.execute(sql, data)
            list_download = utils.cursor_to_download_object(cursor)

            if len(list_download) == 0:
                logging.info('No download found with file_path %s' % file_path)
            elif len(list_download) == 1:
                download = list_download[0]
                utils.log_debug(u'%s download : %s' % (indent_log, download.to_string()))
            else:
                logging.error('Too many download found with file_path %s' % file_path)
        else:
            download = self.get_download_by_id(download_id)

        return download

    def get_downloads_in_progress(self, download_id):
        utils.log_debug(u'*** get_downloads_in_progress ***')
        utils.log_debug(u'download_id: %s' % str(download_id))

        list_downloads = []

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s'
            data = (Download.STATUS_IN_PROGRESS, )
            utils.log_debug(u'query : %s | data : (%s)' % (sql, str(Download.STATUS_IN_PROGRESS)))

            cursor.execute(sql, data)

            list_downloads = utils.cursor_to_download_object(cursor)
        else:
            download = self.get_download_by_id(download_id)
            list_downloads.append(download)

        return list_downloads

    def download_already_exists(self, link):
        utils.log_debug(u'*** download_already_exists ***')

        exists = False
        if link is not None and link != '':
            cursor = self.cnx.cursor()

            sql = 'SELECT id FROM download WHERE link = %s'
            data = (link, )

            utils.log_debug(u'query : %s | data : (%s)' % (sql, link))
            cursor.execute(sql, data)

            if cursor is not None:
                for (download_id) in cursor:
                    utils.log_debug(u'id: %s' % str(download_id))
                    exists = True

                cursor.close()

            utils.log_debug(u'download exists ? %s' % str(exists))
        else:
            logging.error('Link is none')

        return exists

    def insert_update_download(self, link, file_path):
        utils.log_debug(u'*** insert_update_download ***')

        # si la ligne n'est pas marque comme termine avec ce programme
        if not link.startswith(self.MARK_AS_FINISHED):
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
                utils.log_debug(u'Download %s exists -> update' % link)
                download = self.get_download_by_link_file_path(link, file_path)

                if download is not None and download.status != Download.STATUS_FINISHED:
                    if download.name is None or download.name == '':
                        utils.log_debug(u'command : %s' % cmd)
                        name, size = utils.get_infos_plowprobe(cmd)
                        utils.log_debug(u'Infos get from plowprobe %s,%s' % (
                            name, size))

                    if finished:
                        download.status = Download.STATUS_FINISHED

                    download.infos_plodown = 'updated by insert_update_download method\r\n'
                    self.update_download(download)

    def stop_download(self, download):
        utils.log_debug(u'*** stop_download ***')
        utils.log_debug(u'pid python: %s' % str(download.pid_python))
        utils.kill_proc_tree(download.pid_python)

        download.pid_python = 0
        download.pid_plowdown = 0
        download.status = Download.STATUS_WAITING
        download.infos_plodown = 'updated by stop_download method\r\n'
        self.update_download(download)

    def start_download(self, download):
        utils.log_debug(u'*** start_download ***')
        indent_log = '  '

        cmd = (
            self.COMMAND_DOWNLOAD % (
                self.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, self.DIRECTORY_DOWNLOAD_DESTINATION, download.link))
        utils.log_debug(u'%s command : %s' % (indent_log, cmd))
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        download.pid_plowdown = p.pid
        download.pid_python = os.getpid()
        download.status = Download.STATUS_IN_PROGRESS
        download.infos_plodown = 'updated by start_download method\r\n'
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
        utils.log_debug(u'*** get_download_values ***')

        values = values_line.split()
        print(values_line)

        if len(values) > 0:
            utils.log_debug(u"values[0]: %s" % str(values[0]))
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
                download.size_file_downloaded = download.size_previous_part_downloaded + download.size_part_downloaded

                # average speed
                download.average_speed = utils.compute_size(values[6])

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
                download.name = tab_name[len(tab_name) - 1]

            download.infos_plowdown = time.strftime('%d/%m/%y %H:%M:%S',
                                                    time.localtime()) + ': ' + values_line + '\r\n'
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
            download.infos_plowdown = 'updated by check_download_alive_method\r\nProcess killed by inactivity ...\r\n'

            self.update_download(download)

    def disconnect(self):
        utils.log_debug(u'*** disconnect ***')

        self.cnx.close()
        # self.ws.close()
