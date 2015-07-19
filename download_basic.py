#!/usr/bin/env python

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
# import time


# class NotificationServer(WebSocketServerProtocol):
# def onConnect(self, request):
# logging.debug("Client connecting: {}".format(request.peer))
# print("Client connecting: {}".format(request.peer))
#
# def onOpen(self):
#         print("WebSocket connection open.")
#
#     def onMessage(self, payload, isBinary):
#         if isBinary:
#             logging.debug("Binary message received: {} bytes".format(len(payload)))
#             print("Binary message received: {} bytes".format(len(payload)))
#         else:
#             logging.debug("Text message received: {}".format(payload.decode('utf8')))
#             print("Text message received: {}".format(payload.decode('utf8')))
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
    COMMAND_DOWNLOAD = "plowdown -r 10 -x -m --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory %s -o %s %s"
    COMMAND_DOWNLOAD_INFOS = "plowprobe --printf '# {\"name\":\"%f\",\"size\":\"%s\"}' "

    def __init__(self):
        self.cnx = utils.database_connect()
        self.stop_loop_file_treatment = False

    def get_download_to_start(self, download_id):
        logging.debug('*** get_download_to_start ***')
        logging.debug('download_id: %s' % str(download_id))
        download = None

        cursor = self.cnx.cursor()

        if download_id is None:
            sql = 'SELECT * FROM download WHERE status = %s HAVING MIN(id)'
            data = (Download.STATUS_WAITING, )
            logging.debug('query : %s | data : (%s)' % (sql, str(Download.STATUS_WAITING)))
        else:
            sql = 'SELECT * FROM download WHERE id = %s'
            data = (download_id, )
            logging.debug('query : %s | data : (%s)' % (sql, str(download_id)))

        cursor.execute(sql, data)

        if cursor is not None:
            for (database_download_id, name, link, origin_size, size, status, progress, average_speed, time_left,
                 pid_plowdown, pid_curl, pid_python, file_path) in cursor:
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
                download.file_path = file_path

                logging.debug('download : %s' % download.to_string())

            cursor.close()

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

        if cursor is not None:
            for (database_download_id, name, link, origin_size, size, status, progress, average_speed, time_left,
                 pid_plowdown, pid_curl, pid_python, file_path) in cursor:
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
                download.file_path = file_path

                logging.debug('download : %s' % download.to_string())

                list_downloads.append(download)

            cursor.close()

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

        replace_string = "# " + download.name + "\r\n# " + download.link
        new_data = file_data.replace(download.link, replace_string)

        f = open(download.file_path, 'w')
        f.write(new_data)
        f.close()

    def insert_download(self, link, file_path):
        logging.debug('*** insert_download ***')

        if not self.download_already_exists(link):
            logging.debug('download %s doesn''t exist' % link)

            cursor = self.cnx.cursor()

            sql = 'INSERT INTO download (link, status, file_path) values (%s, %s, %s)'
            data = (link, Download.STATUS_WAITING, file_path)
            logging.debug('query: %s | data: (%s, %s, %s)' % (sql, link, Download.STATUS_WAITING, file_path))

            cursor.execute(sql, data)

            cursor.close()

    def update_download_values(self, download):
        logging.debug('*** update_download_values ***')

        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET name = %s, origin_size = %s, size = %s, progress = %s, average_speed = %s, time_left = %s ' \
              + 'WHERE id = %s'
        data = (download.name,
                download.origin_size, download.size, download.progress, download.average_speed, download.time_left,
                download.id)
        logging.debug('query : %s | data : (%s, %s, %s, %s, %s, %s, %s)' % (
            sql, download.name, str(download.origin_size), str(download.size), str(download.progress),
            str(download.average_speed),
            str(download.time_left),
            str(download.id)))
        cursor.execute(sql, data)

        cursor.close()

    def update_download_pid(self, pid_plowdown, pid_python, download_id, status):
        logging.debug('*** update_download_pid ***')

        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET pid_plowdown = %s, pid_python = %s, status = %s WHERE id = %s'
        data = (pid_plowdown, pid_python, status, download_id)
        logging.debug('query : %s | data : (%s, %s, %s, %s)' % (
            sql, str(pid_plowdown), pid_python, str(status), str(download_id)))
        cursor.execute(sql, data)
        cursor.close()

    def stop_download(self, download):
        logging.debug('*** stop_download ***')
        logging.debug('pid python: ' + str(download.pid_python))

        self.update_download_pid(0, 0, download.id, Download.STATUS_WAITING)
        utils.kill_proc_tree(download.pid_python)

    def start_download(self, download):
        logging.debug('*** start_download ***')

        cmd = (
            self.COMMAND_DOWNLOAD % (
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
                    download = self.get_download_values(line, download)
                    line = ''

        return download

    def start_file_treatment(self, file_path):
        logging.debug('*** start_file_treatment ***')

        # insert links in database
        file = open(file_path, 'r')
        logging.debug('file %s opened' % file_path)
        for line in file:
            if line.startswith('http'):
                logging.debug('line start with http')
                self.insert_download(line, file_path)
        file.close()

        download = self.get_download_to_start(None)
        while not self.stop_loop_file_treatment and download is not None:
            download = self.start_download(download)
            # mark link with # in file
            if download.status == Download.STATUS_FINISHED:
                self.mark_link_finished_in_file(download)

            # next download
            download = self.get_download_to_start(None)

    def stop_file_treatment(self, file_path):
        logging.debug('*** stop_file_treatment ***')

        # TODO: stop current download
        self.stop_loop_file_treatment = True

    def get_download_values(self, values_line, download):
        logging.debug('*** get_download_values ***')

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

                self.update_download_values(download)
            elif "Filename" in values[0]:
                tab_name = values_line.split('Filename:')
                download.name = tab_name[len(tab_name) - 1]

        return download

    def check_download_alive(self, download):
        logging.debug('*** check_download_alive ***')

        if not utils.check_pid(download.pid_plowdown):
            utils.kill_proc_tree(download.pid_python)
            self.update_download_pid(0, 0, download.id, Download.STATUS_WAITING)

    def disconnect(self):
        logging.debug('*** disconnect ***')

        self.cnx.close()


COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    logging.basicConfig(filename='/var/www/log.log', level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    # log.startLogging(sys.stdout)

    logging.debug('Start application')
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
        logging.debug('args[0]: %s' % args[0])
        logging.debug('args length: %s' % str(len(args)))
        # start a download
        if args[0] == 'start':
            if len(args) > 1:
                logging.debug('args[1]: %s' % str(args[1]))
                download_id = args[1]
                # print(time.ctime())
                # time.sleep(30)
                # print(time.ctime())
                # print("sending start")
                # factory.protocol.sendMessage('staaaaaaaaaaaaaaart')
                logging.debug('download_id %s' % download_id)
                download_to_start = manage_download.get_download_to_start(download_id)
                logging.debug('download to start %s' % download_to_start.to_string())
                manage_download.start_download(download_to_start)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            if len(args) > 1:
                download_id = args[1]
                logging.debug('download_id %s' % download_id)
                download_to_start = manage_download.get_download_to_start(download_id)
                logging.debug('download to stop %s' % download_to_start.to_string())
                manage_download.stop_download(download_to_start)
            else:
                print(COMMAND_USAGE)
        # start downloads from file
        elif args[0] == 'start_file':
            if len(args) > 1:
                file_path = args[1]
                logging.debug('file path containing links %s', file_path)
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
                logging.debug('download_id %s' % download_to_check.id)
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