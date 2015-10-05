__author__ = 'Vincent'

import subprocess
import re

import psutil
from mysql.connector import (connection)
from bean.downloadBean import Download
from bean.downloadPackageBean import DownloadPackage
import logging

REST_ADRESSE = 'http://localhost:3000/'

MYSQL_LOGIN = 'root'
MYSQL_PASS = 'capic_20_04_1982'
MYSQL_HOST = '192.168.1.101'
MYSQL_DATABASE = 'plowshare'

DIRECTORY_WEB_LOG = '.'
DIRECTORY_DOWNLOAD_DESTINATION_TEMP = '/mnt/HD/HD_a2/telechargement/temp_plowdown/'
DIRECTORY_DOWNLOAD_DESTINATION = '/mnt/HD/HD_a2/telechargement/'

LOG_OUTPUT = True
CONSOLE_OUTPUT = True


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

    return int(size_number)


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
    log_debug(u'Command plowprobe %s' % cmd)
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('UTF-8')

    if output.startswith('==>'):
        tab_infos = output.split('=$=')
        name = tab_infos[0].replace('==>', '')
        log_debug('name before modification %s' % name)
        name = clean_string_console(name)
        log_debug('name after modification %s' % name)

        size = 0
        if tab_infos[1] is not None and tab_infos[1] != '':
            size = int(tab_infos[1])
            log_debug(u'Size %s' % str(size))

        return [name, size]
    else:
        return [None, None]


def clean_string_console(string):
    string = string.strip()
    string = string.replace("\033\[[0-9;]+m", '')
    string = string.replace("\033", '')

    return string


def json_to_download_object(json_object):
    download = Download()
    download.id = json_object['id']
    download.name = json_object['name']
    if json_object['package_id'] != 'null':
        download_package = DownloadPackage()
        download_package.id = json_object['download_package']['id']
        download_package.name = json_object['download_package']['name']
        download_package.unrar_progress = json_object['download_package']['unrar_progress']
        download.package = download_package
    else:
        download.package = None
    download.link = json_object['link']
    download.size_file = json_object['size_file']
    download.size_part = json_object['size_part']
    download.size_file_downloaded = json_object['size_file_downloaded']
    download.size_part_downloaded = json_object['size_part_downloaded']
    download.status = json_object['status']
    download.progress_part = json_object['progress_part']
    download.average_speed = json_object['average_speed']
    download.current_speed = json_object['current_speed']
    download.time_spent = json_object['time_spent']
    download.time_left = json_object['time_left']
    download.pid_plowdown = json_object['pid_plowdown']
    download.pid_python = json_object['pid_python']
    download.file_path = json_object['file_path']
    download.priority = json_object['priority']
    if json_object['theorical_start_datetime'] == 0:
        download.theorical_start_datetime = None
    else:
        download.theorical_start_datetime = json_object['theorical_start_datetime']
    if json_object['lifecycle_insert_date'] == 0:
        download.lifecycle_insert_date = None
    else:
        download.lifecycle_insert_date = json_object['lifecycle_insert_date']
    if json_object['lifecycle_update_date'] == 0:
        download.lifecycle_update_date = None
    else:
        download.lifecycle_update_date = json_object['lifecycle_update_date']

    return download

def json_to_download_object_list(json_array):
    list_downloads = []

    for json_object in json_array:
        download = json_to_download_object(json_object)
        list_downloads.append(download)

    return list_downloads


def json_to_download_package_object(json_object):
    download_package = DownloadPackage()
    download_package.id = json_object['id']
    download_package.name = json_object['name']
    download_package.unrar_percent = json_object['unrar_percent']

    return download

def package_name_from_download_name(download_name):
    ext = download_name.split(".")[-1]

    if ext == 'rar':
        return download_name.split(".part")[0]
    else:
        return None


def log_debug(value):
    if LOG_OUTPUT:
        logging.debug(value)

    if CONSOLE_OUTPUT:
        print(value)
