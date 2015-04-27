#!/usr/bin/env python

__author__ = 'Vincent'

import os
import subprocess
import sys
import getopt
import logging
from bean.downloadBean import Download
import utils


class ManageDownloads:
    DIRECTORY_DOWNLOAD_DESTINATION_TEMP = "/mnt/HD/HD_a2/telechargement/temp_plowdown/"
    DIRECTORY_DOWNLOAD_DESTINATION = "/mnt/HD/HD_a2/telechargement/"
    COMMAND = "plowdown -r 10 -x -m --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"

    def __init__(self):
        self.cnx = utils.database_connect()

    def get_download_to_start(self, download_id):
        download = None

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s HAVING MIN(id)'
            data = (Download.STATUS_WAITING, )
            cursor.execute(sql, data)
        else:
            sql = 'SELECT * FROM download WHERE id = %s'
            data = (download_id, )
            cursor.execute(sql, data)

        if cursor is not None:
            for (database_download_id, name, link, origin_size, size, status, progress, average_speed, time_left,
                 pid_plowdown, pid_curl, pid_python) in cursor:
                download = Download()
                download.id = database_download_id
                download.name = name
                download.link = link
                download.origin_size = origin_size
                download.size = size
                download.status = status
                download.progress = progress
                download.average_speed = average_speed
                download.time_left = time_left
                download.pid_plowdown = pid_plowdown
                download.pid_python = pid_python

        cursor.close()

        return download

    def update_download_values(self, download):
        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET origin_size = %s, size = %s, progress = %s, average_speed = %s, time_left = %s ' \
              + 'WHERE id = %s'
        data = (
            download.origin_size, download.size, download.progress, download.average_speed, download.time_left,
            download.id)
        logging.debug('query : %s | data : (%s, %s, %s, %s, %s, %s)' % (
            sql, str(download.origin_size), str(download.size), str(download.progress), str(download.average_speed),
            str(download.time_left),
            str(download.id)))
        cursor.execute(sql, data)

        cursor.close()

    def update_download_pid(self, pid_plowdown, pid_python, download_id, status):
        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET pid_plowdown = %s, pid_python = %s, status = %s WHERE id = %s'
        data = (pid_plowdown, pid_python, status, download_id)
        logging.debug('query : %s | data : (%s, %s, %s, %s)' % (
            sql, str(pid_plowdown), pid_python, str(status), str(download_id)))
        cursor.execute(sql, data)
        cursor.close()

    def stop_download(self, download):
        logging.debug('--- stop_download ---')
        logging.debug('pid python: ' + str(download.pid_python))

        self.update_download_pid(0, 0, download.id, Download.STATUS_WAITING)
        utils.kill_proc_tree(download.pid_python)

    def start_download(self, download):
        logging.debug('--- start_download ---')

        cmd = (
            self.COMMAND % (
                self.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, self.DIRECTORY_DOWNLOAD_DESTINATION, download.link))
        logging.debug('command : %s' % cmd)
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        self.update_download_pid(p.pid, os.getpid(), download.id, Download.STATUS_IN_PROGRESS)

        line = ''
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() is not None:
                break
            if out != '':
                if out != '\n' and out != '\r':
                    line += out
                else:
                    logging.debug('plowdown line : %s' % line)
                    self.get_download_values(line, download)
                    line = ''

    def get_download_values(self, values_line, download):
        values = values_line.split()

        if len(values) > 0 and values[0].isdigit():
            download.progress = values[0]
            if download.origin_size is None or download.origin_size == 0:
                logging.debug('origin size to compute : ' + values[1])
                download.origin_size = utils.compute_size(values[1])
            logging.debug('size to compute : ' + values[1])
            download.size = utils.compute_size(values[1])
            logging.debug('average_speed to compute : ' + values[6])
            download.average_speed = utils.compute_size(values[6])
            download.id = 1
            if '-' not in values[10]:
                download.time_left = utils.hms_to_seconds(values[10])

            self.update_download_values(download)

    def disconnect(self):
        self.cnx.close()


COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    logging.basicConfig(filename='/var/www/log.log', level=logging.DEBUG)

    try:
        opts, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        print(COMMAND_USAGE)

    download_id = None
    if len(args) == 0:
        print(COMMAND_USAGE)
    else:
        if len(args) > 1:
            download_id = args[1]

        manage_download = ManageDownloads()
        logging.debug('download_id %s' % download_id)
        download_to_start = manage_download.get_download_to_start(download_id)
        logging.debug('download to start %s' % download_to_start.to_string())

        if download_to_start is not None:
            if args[0] == 'start':
                manage_download.start_download(download_to_start)
            elif args[0] == 'stop':
                manage_download.stop_download(download_to_start)
            else:
                print(COMMAND_USAGE)

        manage_download.disconnect()

if __name__ == "__main__":
    main(sys.argv[1:])