__author__ = 'Vincent'

import psutil
import subprocess
import re
from mysql.connector import (connection)
from bean.downloadBean import Download

MYSQL_LOGIN = 'root'
MYSQL_PASS = 'capic_20_04_1982'
MYSQL_HOST = '127.0.0.1'
MYSQL_DATABASE = 'plowshare'


def database_connect():
    return connection.MySQLConnection(user=MYSQL_LOGIN, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_DATABASE)

def hms_to_seconds(t):
    h, m, s = [int(i) for i in t.split(':')]
    return int(3600 * h + 60 * m + s)


def compute_size(s):
    if len(s) > 1:
        size_letter = s[-1:].lower()
        size_number = float(s[:-1])

        if size_letter == 'k':
            size_number *= 1024
        elif size_letter == 'm':
            size_number *= 1024 * 1024
    else:
        size_number = int(s)

    return size_number


def kill_proc_tree(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        if including_parent:
            parent.kill()
    except psutil.NoSuchProcess:
        pass


def check_pid(pid):
    return psutil.pid_exists(pid)


def clean_plowdown_line(line):
    idxs = [m.start() for m in re.finditer('\[0', line)]

    n = 0
    if len(idxs) > 0:
        for idx in idxs:
            if idx == 1:
                if line[2] == ';':
                    n = 9
                    line = line[n:]
                else:
                    n = 7
                    line = line[n:]
            else:
                line = line[:idx - n]

    return line


def get_infos_plowprobe(cmd):
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

    tab_infos = output.split('=$=')
    name = tab_infos[0]

    size = 0
    if tab_infos[1] is not None and tab_infos[1] != '':
        size = int(tab_infos[1])

    return [name, size]


def cursor_to_download_object(cursor):
    list_downloads = []

    if cursor is not None:
        for (database_download_id, name, package, link, size_file, size_part, size_file_downloaded, size_part_downloaded,
             status, progress_part, average_speed, time_spent, time_left, pid_plowdown, pid_curl, pid_python, file_path,
             priority, infos_plowdown, lifecycle_insert_date, lifecycle_update_date) in cursor:

            download = Download()
            download.id = database_download_id
            download.name = name
            download.package = package
            download.link = link
            download.size_file = size_file
            download.size_part = size_part
            download.size_file_downloaded = size_file_downloaded
            download.size_part_downloaded = size_part_downloaded
            download.status = status
            download.progress_part = progress_part
            download.average_speed = average_speed
            download.time_spent = time_spent
            download.time_left = time_left
            download.pid_plowdown = pid_plowdown
            download.pid_python = pid_python
            download.file_path = file_path
            download.priority = priority
            download.infos_plowdown = infos_plowdown
            download.lifecycle_insert_date = lifecycle_insert_date
            download.lifecycle_update_date = lifecycle_update_date

            list_downloads.append(download)

        cursor.close()

    return list_downloads


def package_name_from_download_name(download_name):
    ext = download_name.split(".")[-1]

    if ext == 'rar':
        return download_name.split(".part")[0]
    else:
        return download_name