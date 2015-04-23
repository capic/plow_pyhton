__author__ = 'Vincent'

import subprocess, sys, getopt
from bean.downloadBean import Download
import utils
from mysql.connector import (connection)


class ManageDownloads:
    def __init__(self):
        self.cnx = utils.database_connect()

    def get_download_to_start(self):
        download = None

        cursor = self.cnx.cursor()

        sql = 'SELECT * FROM download WHERE status = %s HAVING MIN(id)'
        data = (Download.STATUS_WAITING, )
        cursor.execute(sql, data)

        for (download_id, name, link, origin_size, size, status, progress, average_speed, time_left, pid_plowdown, pid_curl) in cursor:
            download = Download()
            download.id = download_id
            download.name = name
            download.link = link
            download.origin_size = origin_size
            download.size = size
            download.status = status
            download.progress = progress
            download.average_speed = average_speed
            download.time_left = time_left

        cursor.close()

        return download

    def update_download_values(self, download):
        cursor = self.cnx.cursor()

        sql = 'UPDATE download SET size = %s, progress = %s, average_speed = %s, time_left = %s ' \
              + ' WHERE id = %s'
        data = (download.size, download.progress, download.average_speed, download.time_left, download.id)
        cursor.execute(sql, data)
        cursor.close()

    def start_download(self, download):
        cmd = "plowdown " + download.link
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
                    self.get_download_values(line)
                    line = ''

    def get_download_values(self, values_line):
        values = values_line.split()

        if len(values) > 0 and values[0].isdigit():
            download = Download()
            download.progress = values[0]
            download.size = utils.compute_size(values[1])
            download.average_speed = utils.compute_size(values[6])
            download.id = 1
            if '-' not in values[10]:
                download.time_left = utils.hms_to_seconds(values[10])

            self.update_download_values(download)

    def disconnect(self):
        self.cnx.close()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hl:p:k:u:o:", ["login=", "password=", "sheetkey=", "sheeturl", "outputdirectory="])
    except getopt.GetoptError:
        print ''

    manage_download = ManageDownloads()
    download_to_start = manage_download.get_download_to_start()

    if download_to_start is not None:
        manage_download.start_download(download_to_start)

    manage_download.disconnect()

if __name__ == "__main__":
    main(sys.argv[1:])