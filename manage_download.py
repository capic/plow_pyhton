#!/usr/bin/env python

__author__ = 'Vincent'

import logging
import utils
import os
import subprocess
import time
from datetime import datetime
from bean.downloadBean import Download


class ManageDownloads:
    DIRECTORY_DOWNLOAD_DESTINATION_TEMP = "/mnt/HD/HD_a2/telechargement/temp_plowdown/"
    DIRECTORY_DOWNLOAD_DESTINATION = "/mnt/HD/HD_a2/telechargement/"
    COMMAND_DOWNLOAD = "/usr/bin/plowdown -r 10 -x --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"
    COMMAND_DOWNLOAD_INFOS = "/usr/bin/plowprobe --printf '%%f=$=%%s' %s"

    def __init__(self):
        self.cnx = utils.database_connect()

    def insert_download(self, download):
        logging.debug('  *** insert_download ***')
        indent_log = '   '

        if download is not None:
            cursor = self.cnx.cursor()

            sql = 'INSERT INTO download (name, link, size_file, status, file_path, priority, lifecycle_insert_date) values (%s, %s, %s, %s, %s, %s, %s)'
            data = (
                download.name, download.link, download.size_file, download.status, download.file_path,
                download.priority,
                datetime.now())
            logging.debug(
                '%s query: %s | data: (%s, %s, %s, %s, %s, %s)' % (
                    indent_log, sql, download.name.encode('UTF-8'), download.link.encode('UTF-8'),
                    str(download.size).encode('UTF-8'),
                    str(download.priority).encode('UTF-8'), download.file_path.encode('UTF-8'),
                    str(datetime.now()).encode('UTF-8'),))

            cursor.execute(sql, data)

            cursor.close()
        else:
            logging.error("Download is none")

    def update_download(self, download):
        logging.debug('  *** update_download ***')
        indent_log = '   '

        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET name = %s, link = %s, size_file = %s, size_part = %s, size_file_downloaded = %s, size_part_downloaded = %s,' \
              'status = %s, progress_part = %s, average_speed = %s, time_spent = %s, time_left = %s , pid_plowdown = %s, pid_python = %s, priority = %s, ' \
              'file_path = %s, infos_plowdown = concat(ifnull(infos_plowdown,""), %s), lifecycle_update_date = %s WHERE id = %s'
        data = (download.name, download.link, download.size_file, download.size_part, download.size_file_downloaded,
                download.size_part_downloaded, download.status, download.progress_part, download.average_speed,
                download.time_spent, download.time_left, download.pid_plowdown, download.pid_python, download.priority,
                download.file_path, download.infos_plowdown, datetime.now(), download.id)
        logging.debug(
            '%s query : %s | data : (%s, %s, %s, %s, %s,%s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (
                indent_log, sql, download.name.encode('UTF-8'), download.link.encode('UTF-8'),
                str(download.size_file).encode('UTF-8'), str(download.size_part).encode('UTF-8'),
                str(download.size_file_downloaded).encode('UTF-8'), str(download.size_part_downloaded).encode('UTF-8'),
                str(download.status).encode('UTF-8'), str(download.progress_part).encode('UTF-8'),
                str(download.average_speed).encode('UTF-8'), str(download.time_spent).encode('UTF-8'),
                str(download.time_left).encode('UTF-8'),
                str(download.pid_plowdown).encode('UTF-8'), str(download.pid_python).encode('UTF-8'),
                str(download.priority),
                download.file_path.encode('UTF-8'),
                download.infos_plowdown.encode('UTF-8'),
                str(datetime.now()).encode('UTF-8'), str(download.id).encode('UTF-8')))
        cursor.execute(sql, data)

        cursor.close()

    def get_download_by_id(self, download_id):
        logging.debug('   *** get_download_by_id ***')
        indent_log = '   '
        download = None

        if id is not None:
            cursor = self.cnx.cursor()

            sql = 'SELECT * FROM download WHERE id = %s'
            data = (download_id, )
            logging.debug('%s query : %s | data : (%s)' % (indent_log, sql, str(download_id).encode('UTF-8')))

            cursor.execute(sql, data)

            list_download = utils.cursor_to_download_object(cursor)

            if len(list_download) == 0:
                logging.info('No download fouud with id %s' % download_id)
            elif len(list_download) == 1:
                download = list_download[0]
                logging.debug('%s download : %s' % (indent_log, download.to_string().encode('UTF-8')))
            else:
                logging.error('Too many download found with id %s' % download_id)
        else:
            logging.error('Id is none')

        return download

    def get_download_by_link_file_path(self, link, file_path):
        logging.debug('   *** get_download_by_link_file_path ***')
        indent_log = '   '

        logging.debug('%s link: %s, file_path: %s' % (indent_log, link.encode('UTF-8'), file_path.encode('UTF-8')))

        download = None

        if link is not None and link != '' and file_path is not None and file_path != '':
            cursor = self.cnx.cursor()
            sql = 'SELECT * FROM download WHERE link = %s and file_path = %s'
            data = (link, file_path)
            logging.debug(
                '%s query : %s | data : (%s, %s)' % (indent_log, sql, link.encode('UTF-8'), file_path.encode('UTF-8')))

            cursor.execute(sql, data)

            list_download = utils.cursor_to_download_object(cursor)

            if len(list_download) == 0:
                logging.info('No download fouud with link %s and file_path %s' % (link, file_path))
            elif len(list_download) == 1:
                download = list_download[0]
                logging.debug('%s download : %s' % (indent_log, download.to_string().encode('UTF-8')))
            else:
                logging.error('Too many download found with link %s and file_path %s' % (link, file_path))

        return download

    def get_download_to_start(self, download_id, file_path=None):
        logging.debug(' *** get_download_to_start ***')
        indent_log = ' '
        logging.debug(' %s download_id: %s' % (indent_log, str(download_id).encode('UTF-8')))

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

                logging.debug(
                    '%s query : %s | data : (%s, %s, %s, %s)' % (
                        indent_log, sql, str(Download.STATUS_WAITING).encode('UTF-8'), file_path.encode('UTF-8'),
                        str(Download.STATUS_WAITING).encode('UTF-8'), file_path.encode('UTF-8')))
            else:
                sql += ' AND priority = (' + under_sql + ')'

                data = (Download.STATUS_WAITING, Download.STATUS_WAITING)
                logging.debug(
                    '%s query : %s | data : (%s, %s)' % (indent_log, sql, str(Download.STATUS_WAITING).encode('UTF-8'),
                                                         str(Download.STATUS_WAITING).encode('UTF-8')))

            sql += ' HAVING  MIN(id)'

            cursor.execute(sql, data)
            list_download = utils.cursor_to_download_object(cursor)

            if len(list_download) == 0:
                logging.info('No download found with file_path %s' % file_path)
            elif len(list_download) == 1:
                download = list_download[0]
                logging.debug('%s download : %s' % (indent_log, download.to_string().encode('UTF-8')))
            else:
                logging.error('Too many download found with file_path %s' % file_path)
        else:
            download = self.get_download_by_id(download_id)

        return download

    def get_downloads_in_progress(self, download_id):
        logging.debug('*** get_downloads_in_progress ***')
        logging.debug('download_id: %s' % str(download_id).encode('UTF-8'))

        list_downloads = []

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s'
            data = (Download.STATUS_IN_PROGRESS, )
            logging.debug('query : %s | data : (%s)' % (sql, str(Download.STATUS_IN_PROGRESS).encode('UTF-8')))

            cursor.execute(sql, data)

            list_downloads = utils.cursor_to_download_object(cursor)
        else:
            download = self.get_download_by_id(download_id)
            list_downloads.append(download)

        return list_downloads

    def download_already_exists(self, link):
        logging.debug('*** download_already_exists ***')

        exists = False
        if link is not None and link != '':
            cursor = self.cnx.cursor()

            sql = 'SELECT id FROM download WHERE link = %s'
            data = (link, )

            logging.debug('query : %s | data : (%s)' % (sql, link.encode('UTF-8')))
            cursor.execute(sql, data)

            if cursor is not None:
                for (download_id) in cursor:
                    logging.debug('id: %s' % str(download_id).encode('UTF-8'))
                    exists = True

                cursor.close()

            logging.debug('download exists ? %s' % str(exists).encode('UTF-8'))
        else:
            logging.error('Link is none')

        return exists

    def insert_update_download(self, link, file_path):
        logging.debug('  *** insert_update_download ***')
        indent_log = '  '

        # si la ligne n'est pas marque comme termine avec ce programme
        if not link.startswith('# '):
            finished = False
            # si la ligne est marque comme termine par le traitement par liste de plowdown
            if link.startswith('#OK'):
                finished = True
                link = link.replace('#OK ', '')

            cmd = (self.COMMAND_DOWNLOAD_INFOS % link)
            exists = self.download_already_exists(link)
            # on n'insere pas un lien qui existe deja ou qui est termine
            if not exists:
                logging.debug('%s Download finished ? %s' % (indent_log, str(finished).encode('UTF-8')))
                if not finished:
                    logging.debug('%s Download %s doesn''t exist -> insert' % (indent_log, link.encode('UTF-8')))
                    logging.debug('%s command : %s' % (indent_log, cmd.encode('UTF-8')))

                    name, size = utils.get_infos_plowprobe(cmd)
                    logging.debug('%s Infos get from plowprobe %s,%s' % (
                        indent_log, name.encode('UTF-8'), str(size).encode('UTF-8')))

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
                logging.debug('%s Download %s exists -> update' % (indent_log, link.encode('UTF-8')))
                download = self.get_download_by_link_file_path(link, file_path)

                if download is not None and download.status != Download.STATUS_FINISHED:
                    if download.name is None or download.name == '':
                        logging.debug('%s command : %s' % (indent_log, cmd.encode('UTF-8')))
                        name, size = utils.get_infos_plowprobe(cmd)
                        logging.debug('%s Infos get from plowprobe %s,%s' % (
                            indent_log, name.encode('UTF-8'), size.encode('UTF-8')))

                    if finished:
                        download.status = Download.STATUS_FINISHED

                    download.infos_plodown = 'updated by insert_update_download method\r\n'
                    self.update_download(download)

    def stop_download(self, download):
        logging.debug('*** stop_download ***')
        logging.debug('pid python: %s' % str(download.pid_python).encode('UTF-8'))
        utils.kill_proc_tree(download.pid_python)

        download.pid_python = 0
        download.pid_plowdown = 0
        download.status = Download.STATUS_WAITING
        download.infos_plodown = 'updated by stop_download method\r\n'
        self.update_download(download)

    def start_download(self, download):
        logging.debug('*** start_download ***')
        indent_log = '  '

        cmd = (
            self.COMMAND_DOWNLOAD % (
                self.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, self.DIRECTORY_DOWNLOAD_DESTINATION, download.link))
        logging.debug('%s command : %s' % (indent_log, cmd.encode('UTF-8')))
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
                    logging.debug('plowdown line : %s' % line.encode('UTF-8'))
                    download = self.get_download_values(line, download)
                    line = ''

        return download

    # 0 => pourcentage, 1 => taille totale, 2 => pourcentage recu, 3 => taille recu, 4 pourcentage transfere, 5 => taille transfere,
    # 6 => vitesse moyenne recu, 7 => vitesse moyenne envoye, 8 => temps total, 9 => temps passe, 10 => temps restant, 11 => vitesse courante
    def get_download_values(self, values_line, download):
        logging.debug('*** get_download_values ***')

        print(values_line)
        values = values_line.split()

        if len(values) > 0:
            logging.debug("values[0]: %s" % str(values[0]).encode('UTF-8'))
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
                    logging.debug('download marked as finished')
                    download.status = Download.STATUS_FINISHED

            elif "Filename" in values[0]:
                tab_name = values_line.split('Filename:')
                download.name = tab_name[len(tab_name) - 1]

            download.infos_plowdown = time.strftime('%d/%m/%y %H:%M:%S',
                                                    time.localtime()) + ': ' + values_line + '\r\n'
            self.update_download(download)

        return download

    def check_download_alive(self, download):
        logging.debug('*** check_download_alive ***')

        if not utils.check_pid(download.pid_plowdown):
            # utils.kill_proc_tree(download.pid_python)
            logging.debug(
                'Process %s for download %s killed for inactivity ...\r\n' % (
                    str(download.pid_python).encode('UTF-8'), download.name.encode('UTF-8')))

            download.pid_plowdown = 0
            download.pid_python = 0
            download.status = Download.STATUS_WAITING
            download.time_left = 0
            download.average_speed = 0
            download.infos_plowdown = 'updated by check_download_alive_method\r\nProcess killed by inactivity ...\r\n'

            self.update_download(download)

    def disconnect(self):
        logging.debug('*** disconnect ***')

        self.cnx.close()
