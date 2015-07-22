#!/usr/bin/env python
from __builtin__ import list

__author__ = 'Vincent'

import os
import subprocess
import sys
import getopt
import logging
from bean.downloadBean import Download
import utils
# from twisted.python import log
# from twisted.internet import reactor
# from autobahn.twisted.websocket import WebSocketServerProtocol
# from autobahn.twisted.websocket import WebSocketServerFactory
# from autobahn.twisted.websocket import WebSocketClientProtocol, \
# WebSocketClientFactory
import time
from datetime import datetime


# class NotificationServer(WebSocketServerProtocol):
# def onConnect(self, request):
# logging.debug("Client connecting: {}".format(request.peer))
# print("Client connecting: {}".format(request.peer))
#
# def onOpen(self):
# print("WebSocket connection open.")
#
# def onMessage(self, payload, isBinary):
# if isBinary:
# logging.debug("Binary message received: {} bytes".format(len(payload)))
# print("Binary message received: {} bytes".format(len(payload)))
# else:
# logging.debug("Text message received: {}".format(payload.decode('utf8')))
# print("Text message received: {}".format(payload.decode('utf8')))
#
#         ## echo back message verbatim
#         self.sendMessage(payload, isBinary)
#
#     def onClose(self, wasClean, code, reason):
#         print("WebSocket connection closed: {}".format(reason))


# class NotificationClient(WebSocketClientProtocol):
#     def onConnect(self, response):
#         print("Connected to Server: {}".format(response.peer))
#         self.sendMessage(u"Hello, world!".encode('utf8'))
#
#     def onMessage(self, payload, isBinary):
#         if isBinary:
#             print("Binary message received: {0} bytes".format(len(payload)))
#         else:
#             print("Text message received: {0}".format(payload.decode('utf8')))


class ManageDownloads:
    DIRECTORY_DOWNLOAD_DESTINATION_TEMP = "/mnt/HD/HD_a2/telechargement/temp_plowdown/"
    DIRECTORY_DOWNLOAD_DESTINATION = "/mnt/HD/HD_a2/telechargement/"
    COMMAND_DOWNLOAD = "/usr/bin/plowdown -r 10 -x --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"
    COMMAND_DOWNLOAD_INFOS = "/usr/bin/plowprobe --printf '%%f=$=%%s' %s"

    def __init__(self):
        self.cnx = utils.database_connect()
        self.stop_loop_file_treatment = False

    def get_download_by_link_file_path(self, link, file_path):
        logging.debug('   *** get_download_by_link_file_path ***')
        indent_log = '   '
        logging.debug('%s link: %s, file_path: %s' % (indent_log, link, file_path))

        download = None

        cursor = self.cnx.cursor()
        sql = 'SELECT * FROM download WHERE link = %s and file_path = %s'
        data = (link, file_path)
        logging.debug('%s query : %s | data : (%s, %s)' % (indent_log, sql, link, file_path))
        cursor.execute(sql, data)

        list_download = utils.cursor_to_download_object(cursor)

        if len(list_download) == 1:
            download = list_download[0]

        logging.debug('%s download : %s' % (indent_log, download.to_string()))

        return download

    def get_download_to_start(self, download_id, file_path=None):
        logging.debug(' *** get_download_to_start ***')
        indent_log = ' '
        logging.debug(' %s download_id: %s' % (indent_log, str(download_id)))

        download = None

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s'

            if file_path is not None:
                sql += ' AND file_path = %s'
                logging.debug(
                    '%s query : %s | data : (%s, %s)' % (indent_log, sql, str(Download.STATUS_WAITING), file_path))
                data = (Download.STATUS_WAITING, file_path)
            else:
                data = (Download.STATUS_WAITING, )
                logging.debug('%s query : %s | data : (%s)' % (indent_log, sql, str(Download.STATUS_WAITING)))

            sql += ' HAVING MIN(id)'

        else:
            sql = 'SELECT * FROM download WHERE id = %s'
            data = (download_id, )
            logging.debug('%s query : %s | data : (%s)' % (indent_log, sql, str(download_id)))

        cursor.execute(sql, data)

        list_download = utils.cursor_to_download_object(cursor)

        if len(list_download) == 1:
            download = list_download[0]

        return download

    def get_downloads_in_progress(self, download_id):
        logging.debug('*** get_downloads_in_progress ***')
        logging.debug('download_id: %s' % str(download_id))

        list_downloads = []

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s'
            data = (Download.STATUS_IN_PROGRESS, )
            logging.debug('query : %s | data : (%s)' % (sql, str(Download.STATUS_IN_PROGRESS)))
        else:
            sql = 'SELECT * FROM download WHERE id = %s'
            data = (download_id, )
            logging.debug('query : %s | data : (%s)' % (sql, str(download_id)))

        cursor.execute(sql, data)

        list_download = utils.cursor_to_download_object(cursor)

        return list_downloads

    def download_already_exists(self, link):
        logging.debug('*** download_already_exists ***')

        cursor = self.cnx.cursor()

        sql = 'SELECT id FROM download WHERE link = %s'
        data = (link, )

        logging.debug('query : %s | data : (%s)' % (sql, link))
        cursor.execute(sql, data)

        exists = False
        if cursor is not None:
            for (download_id) in cursor:
                logging.debug('id: %s' % download_id)
                exists = True

            cursor.close()

        logging.debug('download exists ? %s' % exists)
        return exists

    def mark_link_finished_in_file(self, download):
        logging.debug('*** mark_link_finished_in_file ***')

        f = open(download.file_path, 'r')
        file_data = f.read()
        f.close()

        replace_string = "# " + download.name + "\r\n# OK " + download.link
        new_data = file_data.replace(download.link, replace_string)

        f = open(download.file_path, 'w')
        f.write(new_data)
        f.close()

    def insert_update_download(self, link, file_path):
        logging.debug('  *** insert_update_download ***')
        indent_log = '  '

        # si la ligne n'est pas marqué comme terminé avec ce programme
        if not link.startswith('# '):
            # si la ligne est marqué comme terminé par le traitement par liste de plowdown
            if link.startswith('#OK'):
                finished = True
                link = link.replace('#OK ', '')

            cmd = (self.COMMAND_DOWNLOAD_INFOS % link)
            exists = self.download_already_exists(link)
            # on n'insère pas un lien qui existe déjà ou qui est terminé
            if not exists:
                if not finished:
                    logging.debug('%s Download %s doesn''t exist -> insert' % (indent_log, link))

                    logging.debug('%s command : %s' % (indent_log, cmd))
                    name, size = utils.get_infos_plowprobe(cmd)
                    logging.debug('%s Infos get from plowprobe %s,%s' % (indent_log, name, size))
                    cursor = self.cnx.cursor()

                    sql = 'INSERT INTO download (name, link, size, status, file_path, lifecycle_insert_date) values (%s, %s, %s, %s, %s, %s)'
                    data = (name, link, size, Download.STATUS_WAITING, file_path, datetime.now())
                    logging.debug(
                        '%s query: %s | data: (%s, %s, %s, %s, %s, %s)' % (
                            indent_log, sql, name, link, size, Download.STATUS_WAITING, file_path, str(datetime.now()),))

                    cursor.execute(sql, data)

                    cursor.close()
            else:
                logging.debug('%s Download %s exists -> update' % (indent_log, link))
                download = self.get_download_by_link_file_path(link, file_path)

                if download is not None and download.status != Download.STATUS_FINISHED:
                    if download.name is None or download.name == '':
                        logging.debug('%s command : %s' % (indent_log, cmd))
                        name, size = utils.get_infos_plowprobe(cmd)
                        logging.debug('%s Infos get from plowprobe %s,%s' % (indent_log, name, size))

                    if finished:
                        download.status = Download.STATUS_FINISHED

                    self.update_download(download)

    def update_download(self, download):
        logging.debug('  *** update_download ***')
        indent_log = '   '

        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET name = %s, link = %s, origin_size = %s, size = %s, status = %s, progress = %s, average_speed = %s, time_left = %s ' \
              + ', pid_plowdown = %s, pid_python = %s, file_path = %s, infos_plowdown = concat(ifnull(infos_plowdown,""), %s), lifecycle_update_date = %s WHERE id = %s'
        data = (download.name, download.link, download.origin_size, download.size, download.status, download.progress,
                download.average_speed, download.time_left,
                download.pid_plowdown, download.pid_python, download.file_path, download.infos_plowdown, datetime.now(),
                download.id)
        logging.debug('%s query : %s | data : (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (
            indent_log, sql, download.name, download.link, str(download.origin_size), str(download.size),
            str(download.status),
            str(download.progress), str(download.average_speed), str(download.time_left),
            str(download.pid_plowdown), str(download.pid_python), download.file_path, download.infos_plowdown,
            str(datetime.now()), str(download.id)))
        cursor.execute(sql, data)

        cursor.close()

    def stop_download(self, download):
        logging.debug('*** stop_download ***')
        logging.debug('pid python: ' + str(download.pid_python))
        utils.kill_proc_tree(download.pid_python)

        download.pid_python = 0
        download.pid_plowdown = 0
        download.status = Download.STATUS_WAITING
        self.update_download(download)

    def start_download(self, download):
        logging.debug('*** start_download ***')
        indent_log = '  '

        cmd = (
            self.COMMAND_DOWNLOAD % (
                self.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, self.DIRECTORY_DOWNLOAD_DESTINATION, download.link))
        logging.debug('%s command : %s' % (indent_log, cmd))
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        download.pid_plowdown = p.pid
        download.pid_python = os.getpid()
        download.status = Download.STATUS_IN_PROGRESS
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
                    logging.debug('plowdown line : %s' % line)
                    download = self.get_download_values(line, download)
                    line = ''

        return download

    def start_file_treatment(self, file_path):
        logging.debug(' *** start_file_treatment ***')
        indent_log = ' '

        logging.debug('%s =========> Insert new links or update old in database <=========')
        # insert links in database
        file = open(file_path, 'r')
        for line in file:
            if 'http' in line:
                logging.debug('%s Line %s contains http' % (indent_log, line))
                self.insert_update_download(line, file_path)
        file.close()
        logging.debug('%s =========< End insert new links or update old in database >=========')

        download = self.get_download_to_start(None, file_path)
        while not self.stop_loop_file_treatment and download is not None:
            logging.debug('%s =========> Start new download <=========')
            download = self.start_download(download)
            # mark link with # in file
            if download.status == Download.STATUS_FINISHED:
                self.mark_link_finished_in_file(download)
            logging.debug('%s =========< End download >=========')
            # next download
            download = self.get_download_to_start(None, file_path)

    def stop_file_treatment(self, file_path):
        logging.debug('*** stop_file_treatment ***')

        # TODO: stop current download
        self.stop_loop_file_treatment = True

    def get_download_values(self, values_line, download):
        logging.debug('*** get_download_values ***')

        print(values_line)
        values = values_line.split()

        if len(values) > 0:
            logging.debug("values[0]: %s" % str(values[0]))
            if values[0].isdigit():
                download.progress = int(values[0])

                if download.origin_size is None or download.origin_size == 0:
                    logging.debug('origin size to compute : ' + values[1])
                    download.origin_size = utils.compute_size(values[1])

                logging.debug('size to compute : ' + values[1])
                download.size = utils.compute_size(values[1])

                logging.debug('average_speed to compute : ' + values[6])
                download.average_speed = utils.compute_size(values[6])

                if '-' not in values[10]:
                    download.time_left = utils.hms_to_seconds(values[10])

                if values[1] == values[3] and values[1] != '0':
                    logging.debug('download marked as finisher')
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
            utils.kill_proc_tree(download.pid_python)

            download.pid_plowdown = 0
            download.pid_python = 0
            download.status = Download.STATUS_WAITING
            download.time_left = 0
            download.average_speed = 0
            download.infos_plowdown = 'Process killed by inactivity ...\r\n'

            self.update_download(download)

    def disconnect(self):
        logging.debug('*** disconnect ***')

        self.cnx.close()


COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    logging.basicConfig(filename='/var/www/log.log', level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logging.debug('*** Start application ***')
    indent_log = "";

    try:
        opts, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        print(COMMAND_USAGE)
        exit()

    if len(args) == 0:
        print("Parameters are missing")
        print(COMMAND_USAGE)
        exit()
    else:
        # factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
        # factory.protocol = NotificationServer
        #
        # reactor.listenTCP(9000, factory)
        # reactor.run()

        # factory = WebSocketClientFactory()
        # factory.protocol = NotificationClient
        #
        # reactor.connectTCP("127.0.0.1", 8080, factory)
        # reactor.run()

        manage_download = ManageDownloads()

        # start a download
        if args[0] == 'start':
            if len(args) > 1:
                logging.debug('%s args[1]: %s' % (indent_log, str(args[1])))
                download_id = args[1]
                # print(time.ctime())
                # time.sleep(30)
                # print(time.ctime())
                # print("sending start")
                # factory.protocol.sendMessage('staaaaaaaaaaaaaaart')
                logging.debug('%s download_id %s' % (indent_log, download_id))
                download_to_start = manage_download.get_download_to_start(download_id)
                logging.debug('%s download to start %s' % (indent_log, download_to_start.to_string()))
                manage_download.start_download(download_to_start)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            if len(args) > 1:
                download_id = args[1]
                logging.debug('%s download_id %s' % (indent_log, download_id))
                download_to_start = manage_download.get_download_to_start(download_id)
                logging.debug('%s download to stop %s' % (indent_log, download_to_start.to_string()))
                manage_download.stop_download(download_to_start)
            else:
                print(COMMAND_USAGE)
        # start downloads from file
        elif args[0] == 'start_file':
            if len(args) > 1:
                file_path = args[1]
                logging.debug('%s Start file mode: %s', (indent_log, file_path))
                manage_download.start_file_treatment(file_path)
        # stop downloads from file TODO: don't work
        elif args[0] == 'stop_file':
            if len(args) > 1:
                file_path = args[1]
                logging.debug('file path containing links %s', file_path)
                manage_download.stop_file_treatment(file_path)
        # check download process alive TODO do a script with cron to check
        elif args[0] == 'check_download_alive':
            if len(args) > 1:
                download_id = args[1]
                download_to_check = manage_download.get_downloads_in_progress(download_id)
                manage_download.check_download_alive(download_to_check)
            else:
                downloads = manage_download.get_downloads_in_progress(None)

                for download_to_check in downloads:
                    logging.debug('download_id %s' % download_to_check.id)
                    manage_download.check_download_alive(download_to_check)
        else:
            print(COMMAND_USAGE)

        manage_download.disconnect()

        # close websocket ???


if __name__ == "__main__":
    main(sys.argv[1:])
